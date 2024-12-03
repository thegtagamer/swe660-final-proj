from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from bson import ObjectId  # For ObjectId serialization
from flask_cors import CORS
import time
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")


# MongoDB setup
client = MongoClient("mongodb+srv://adey6:7GvI8KrtEXfBQtvq@swe-project.n3gqd.mongodb.net/?retryWrites=true&w=majority&appName=SWE-project")
db = client.weather_db

# Helper function to serialize MongoDB documents
def serialize_document(doc):
    """
    Converts MongoDB documents to a JSON-serializable format.
    """
    if '_id' in doc:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc


def format_datetime_for_db(dt):
    """
    Converts a datetime object to the string format used in the database.
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# Fetch trends for a given time range
def fetch_trends(start_date, end_date):
    data = list(db.sensor_data.find({"timestamp": {"$gte": start_date, "$lt": end_date}}).sort("timestamp", 1))
    trends = [
        {
            "timestamp": entry.get("timestamp"),
            "temperature": entry.get("temperature"),
            "feels_like": calculate_feels_like(entry.get("temperature", 0), entry.get("humidity", 0)),
        }
        for entry in data
    ]
    return trends

@app.route("/trends/weekly", methods=["GET"])
def weekly_trends():
    try:
        # Define the date range for the past 7 days
        now = datetime.utcnow()
        start_of_week = now - timedelta(days=7)

        # Format dates for MongoDB query
        start_of_week_str = format_datetime_for_db(start_of_week)
        now_str = format_datetime_for_db(now)

        # MongoDB aggregation to group by day
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_of_week_str, "$lt": now_str}
                }
            },
            {
                "$group": {
                    "_id": {"$substr": ["$timestamp", 0, 10]},  # Group by date (YYYY-MM-DD)
                    "avg_temperature": {"$avg": "$temperature"},  # Average temperature for the day
                    "min_temperature": {"$min": "$temperature"},  # Min temperature for the day (optional)
                    "max_temperature": {"$max": "$temperature"},  # Max temperature for the day (optional)
                }
            },
            {"$sort": {"_id": 1}},  # Sort by day
        ]

        # Execute the aggregation pipeline
        results = list(db.sensor_data.aggregate(pipeline))

        # Transform the results into a client-friendly format
        trends = [
            {
                "day": result["_id"],
                "avg_temperature": round(result["avg_temperature"], 2),
                "min_temperature": round(result["min_temperature"], 2),
                "max_temperature": round(result["max_temperature"], 2),
            }
            for result in results
        ]

        if not trends:
            return jsonify({"message": "No data found"}), 404

        return jsonify(trends), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trends/monthly", methods=["GET"])
def monthly_trends():
    try:
        # Define the date range for the past 30 days
        now = datetime.utcnow()
        start_of_month = now - timedelta(days=30)

        # Format dates for MongoDB query
        start_of_month_str = start_of_month.strftime("%Y-%m-%d %H:%M:%S")
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # MongoDB aggregation to group by week
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_of_month_str, "$lt": now_str}
                }
            },
            {
                "$addFields": {
                    "year": {"$year": {"$dateFromString": {"dateString": "$timestamp"}}},
                    "week": {"$week": {"$dateFromString": {"dateString": "$timestamp"}}},
                }
            },
            {
                "$group": {
                    "_id": {"year": "$year", "week": "$week"},  # Group by year and week
                    "avg_temperature": {"$avg": "$temperature"},  # Average temperature for the week
                    "min_temperature": {"$min": "$temperature"},  # Min temperature for the week
                    "max_temperature": {"$max": "$temperature"},  # Max temperature for the week
                }
            },
            {"$sort": {"_id.year": 1, "_id.week": 1}},  # Sort by year and week
        ]

        # Execute the aggregation pipeline
        results = list(db.sensor_data.aggregate(pipeline))

        # Transform the results into a client-friendly format
        trends = [
            {
                "week": f"Week {result['_id']['week']} ({result['_id']['year']})",
                "avg_temperature": round(result["avg_temperature"], 2),
                "min_temperature": round(result["min_temperature"], 2),
                "max_temperature": round(result["max_temperature"], 2),
            }
            for result in results
        ]

        if not trends:
            return jsonify({"message": "No data found"}), 404

        return jsonify(trends), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/trends/yearly", methods=["GET"])
def yearly_trends():
    try:
        # Define the date range for the past 365 days
        now = datetime.utcnow()
        start_of_year = now - timedelta(days=365)

        # Format dates for MongoDB query
        start_of_year_str = start_of_year.strftime("%Y-%m-%d %H:%M:%S")
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # MongoDB aggregation to group by month
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_of_year_str, "$lt": now_str}
                }
            },
            {
                "$addFields": {
                    "year": {"$year": {"$dateFromString": {"dateString": "$timestamp"}}},
                    "month": {"$month": {"$dateFromString": {"dateString": "$timestamp"}}},
                }
            },
            {
                "$group": {
                    "_id": {"year": "$year", "month": "$month"},  # Group by year and month
                    "avg_temperature": {"$avg": "$temperature"},  # Average temperature for the month
                    "min_temperature": {"$min": "$temperature"},  # Min temperature for the month
                    "max_temperature": {"$max": "$temperature"},  # Max temperature for the month
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},  # Sort by year and month
        ]

        # Execute the aggregation pipeline
        results = list(db.sensor_data.aggregate(pipeline))

        # Transform the results into a client-friendly format
        trends = [
            {
                "month": f"{result['_id']['year']}-{result['_id']['month']:02d}",
                "avg_temperature": round(result["avg_temperature"], 2),
                "min_temperature": round(result["min_temperature"], 2),
                "max_temperature": round(result["max_temperature"], 2),
            }
            for result in results
        ]

        if not trends:
            return jsonify({"message": "No data found"}), 404

        return jsonify(trends), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# @app.route("/trends/custom", methods=["GET"])
# def custom_trends():
#     try:
#         start_date = request.args.get("start_date")
#         end_date = request.args.get("end_date")

#         if not start_date or not end_date:
#             return jsonify({"error": "start_date and end_date are required"}), 400

#         start_date = datetime.fromisoformat(start_date)
#         end_date = datetime.fromisoformat(end_date)

#         trends = fetch_trends(start_date, end_date)
#         return jsonify(trends), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# WebSocket Route to Send Latest Temperature on Request
@socketio.on('latest_temperature')
def handle_latest_temperature_request():
    """
    Sends the latest temperature value to the client upon request.
    """
    try:
        # Fetch the latest document from the database
        latest_data = db.sensor_data.find_one(sort=[("timestamp", -1)])
        
        if latest_data:
            # Serialize the data
            serialized_data = serialize_document(latest_data)
            # Prepare response
            response_data = {
                "temperature": serialized_data.get("temperature"),
                "timestamp": serialized_data.get("timestamp"),
                "location": serialized_data.get("location"),
            }
            # Emit the data to the client
            emit("latest_temperature_response", response_data)
        else:
            emit("latest_temperature_response", {"message": "No data available"})
    except Exception as e:
        emit("latest_temperature_response", {"error": str(e)})
        
        
# Helper function to calculate feels like temperature
def calculate_feels_like(temperature, humidity):
    """
    Calculates the 'feels like' temperature based on temperature and humidity.
    A simplified formula is used here for demonstration purposes.
    """
    try:
        # Feels like temperature formula (approximation)
        feels_like = temperature + 0.33 * humidity - 0.7
        return round(feels_like, 2)  # Rounded to 2 decimal places
    except Exception as e:
        print(f"Error calculating feels like temperature: {e}")
        return None

# WebSocket Route to Send Today's Trends with Feels Like Calculation
@socketio.on("today_trends")
def handle_today_trends_request():
    """
    Sends the temperature trends for today, including the calculated "feels like" temperature.
    """
    try:
        # Get the current date and construct the date range for today
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Format the timestamps as strings
        start_of_day_str = start_of_day.strftime("%Y-%m-%d %H:%M:%S")
        end_of_day_str = end_of_day.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"start:{start_of_day} end: ${end_of_day}")

        # Fetch today's data from the database
        today_data = list(
            db.sensor_data.find(
                {
                    "timestamp": {"$gte": start_of_day_str, "$lt": end_of_day_str}
                }
            ).sort("timestamp", 1)
        )

        # Check if data is available
        if not today_data:
            emit("today_trends_response", {"message": "No data available for today"})
            return

        # Prepare trends data
        trends = []
        for entry in today_data:
            temperature = entry.get("temperature", 0)
            humidity = entry.get("humidity", 0)
            feels_like = calculate_feels_like(temperature, humidity)
            trends.append({
                "timestamp": entry.get("timestamp"),
                "temperature": temperature,
                "feels_like": feels_like,
            })

        # Emit trends data to the client
        emit("today_trends_response", {"trends": trends})
    except Exception as e:
        print(f"Error handling today_trends_request: {e}")
        emit("today_trends_response", {"error": str(e)})



# Background Task for Real-Time Temperature Broadcasting
# def broadcast_data():
#     """
#     Broadcasts the latest temperature data to all connected clients in real-time.
#     """
#     while True:
#         try:
#             # Fetch the latest document from the database
#             latest_data = db.sensor_data.find_one(sort=[("timestamp", -1)])
#             if latest_data:
#                 # Serialize the document
#                 serialized_data = serialize_document(latest_data)
                
#                 # Calculate feels like temperature
#                 temperature = serialized_data.get("temperature")
#                 humidity = serialized_data.get("humidity")
#                 feels_like = calculate_feels_like(temperature, humidity) if temperature and humidity else None
                
#                 # Prepare response
#                 response_data = {
#                     "temperature": temperature,
#                     "feels_like": feels_like,
#                     "timestamp": serialized_data.get("timestamp"),
#                     "location": serialized_data.get("location"),
#                 }
#                 # Broadcast the latest temperature data
#                 socketio.emit("latest_temperature_response", response_data, to='/')
#             socketio.sleep(5)  # Poll every 5 seconds
#         except Exception as e:
#             print(f"Error broadcasting data: {e}")

# WebSocket Connection Event
@socketio.on('connect')
def on_connect():
    """
    Handles a new WebSocket connection.
    Sends an initial message to confirm the connection.
    """
    print("Client connected")
    emit("message", {"status": "connected"})

# WebSocket Disconnection Event
@socketio.on('disconnect')
def on_disconnect():
    """
    Handles a WebSocket disconnection event.
    """
    print("Client disconnected")
    emit("message", {"status": "disconnected"})

# Main Entry Point
if __name__ == "__main__":
    """
    Starts the Flask-SocketIO server and the background task.
    """
    socketio.run(app, host="0.0.0.0", port=9080)
