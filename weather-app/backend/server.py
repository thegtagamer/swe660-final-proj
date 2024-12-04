from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from pymongo import MongoClient
from flask_cors import CORS
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")


# MongoDB setup
client = MongoClient("mongodb+srv://adey6:7GvI8KrtEXfBQtvq@swe-project.n3gqd.mongodb.net/?retryWrites=true&w=majority&appName=SWE-project")
db = client.weather_db

# Time Zone Setup
LOCAL_TIMEZONE = pytz.timezone("America/New_York")

def get_localized_time():
    """Return the current time in the America/New_York timezone."""
    return datetime.now(LOCAL_TIMEZONE)

# Helper function to serialize MongoDB documents
def serialize_document(doc):
    if '_id' in doc:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc


def format_datetime_for_db(dt):
    """Converts a datetime object to the string format used in the database."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


# Helper function to calculate feels like temperature
def calculate_feels_like(temperature, humidity):
    """Calculates the 'feels like' temperature based on temperature and humidity."""
    try:
        feels_like = temperature + 0.33 * humidity - 0.7
        return round(feels_like, 1)  # Rounded to 1 decimal place
    except Exception as e:
        print(f"Error calculating feels like temperature: {e}")
        return None


# Fetch trends for a given time range
def fetch_trends(start_date, end_date):
    data = list(db.sensor_data.find({"timestamp": {"$gte": start_date, "$lt": end_date}}).sort("timestamp", 1))
    trends = [
        {
            "timestamp": entry.get("timestamp"),
            "temperature": round(float(entry.get("temperature", 0)), 1),  # Ensure 1 decimal
            "humidity": round(float(entry.get("humidity", 0)), 1),  # Ensure 1 decimal
            "feels_like": calculate_feels_like(
                float(entry.get("temperature", 0)),
                float(entry.get("humidity", 0))
            ),
        }
        for entry in data
    ]
    return trends


@app.route("/trends/weekly", methods=["GET"])
def weekly_trends():
    try:
        # now = datetime.utcnow()
        now = get_localized_time()
        start_of_week = now - timedelta(days=7)

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": format_datetime_for_db(start_of_week), "$lt": format_datetime_for_db(now)}
                }
            },
            {
                "$group": {
                    "_id": {"$substr": ["$timestamp", 0, 10]},  # Group by date (YYYY-MM-DD)
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "min_temperature": {"$min": "$temperature"},
                    "min_humidity": {"$min": "$humidity"},
                    "max_temperature": {"$max": "$temperature"},
                    "max_humidity": {"$max": "$humidity"},
                }
            },
            {"$sort": {"_id": 1}},  # Sort by day
        ]

        results = list(db.sensor_data.aggregate(pipeline))
        trends = [
            {
                "day": result["_id"],
                "avg_temperature": round(result["avg_temperature"], 1),
                "avg_humidity": round(result["avg_humidity"], 1),
                "min_temperature": round(result["min_temperature"], 1),
                "min_humidity": round(result["min_humidity"], 1),
                "max_temperature": round(result["max_temperature"], 1),
                "max_humidity": round(result["max_humidity"], 1),
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
        now = get_localized_time()
        # now = datetime.utcnow()
        start_of_month = now - timedelta(days=30)

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": format_datetime_for_db(start_of_month), "$lt": format_datetime_for_db(now)}
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
                    "_id": {"year": "$year", "week": "$week"},
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "min_temperature": {"$min": "$temperature"},
                    "min_humidity": {"$min": "$humidity"},
                    "max_temperature": {"$max": "$temperature"},
                    "max_humidity": {"$max": "$humidity"},
                }
            },
            {"$sort": {"_id.year": 1, "_id.week": 1}},
        ]

        results = list(db.sensor_data.aggregate(pipeline))
        trends = [
            {
                "week": f"Week {result['_id']['week']} ({result['_id']['year']})",
                "avg_temperature": round(result["avg_temperature"], 1),
                "avg_humidity": round(result["avg_humidity"], 1),
                "min_temperature": round(result["min_temperature"], 1),
                "min_humidity": round(result["min_humidity"], 1),
                "max_temperature": round(result["max_temperature"], 1),
                "max_humidity": round(result["max_humidity"], 1),
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
        # now = datetime.utcnow()
        now = get_localized_time()
        start_of_year = now - timedelta(days=365)

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": format_datetime_for_db(start_of_year), "$lt": format_datetime_for_db(now)}
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
                    "_id": {"year": "$year", "month": "$month"},
                    "avg_temperature": {"$avg": "$temperature"},
                    "avg_humidity": {"$avg": "$humidity"},
                    "min_temperature": {"$min": "$temperature"},
                    "min_humidity": {"$min": "$humidity"},
                    "max_temperature": {"$max": "$temperature"},
                    "max_humidity": {"$max": "$humidity"},
                }
            },
            {"$sort": {"_id.year": 1, "_id.month": 1}},
        ]

        results = list(db.sensor_data.aggregate(pipeline))
        trends = [
            {
                "month": f"{result['_id']['year']}-{result['_id']['month']:02d}",
                "avg_temperature": round(result["avg_temperature"], 1),
                "avg_humidity": round(result["avg_humidity"], 1),
                "min_temperature": round(result["min_temperature"], 1),
                "min_humidity": round(result["min_humidity"], 1),
                "max_temperature": round(result["max_temperature"], 1),
                "max_humidity": round(result["max_humidity"], 1),
            }
            for result in results
        ]

        if not trends:
            return jsonify({"message": "No data found"}), 404

        return jsonify(trends), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on("latest_temperature")
def handle_latest_temperature_request():
    try:
        latest_data = db.sensor_data.find_one(sort=[("timestamp", -1)])
        if latest_data:
            response_data = {
                "temperature": round(float(latest_data.get("temperature", 0)), 1),
                "humidity": round(float(latest_data.get("humidity", 0)), 1),
                "timestamp": latest_data.get("timestamp"),
                "location": latest_data.get("location"),
            }
            emit("latest_temperature_response", response_data)
        else:
            emit("latest_temperature_response", {"message": "No data available"})
    except Exception as e:
        emit("latest_temperature_response", {"error": str(e)})
        
        
@socketio.on("today_trends")
def handle_today_trends_request():
    """
    Sends the temperature and humidity trends for today.
    """
    try:
        # Get the current date and construct the date range for today
        now = get_localized_time()
        # now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        # Format the timestamps as strings
        start_of_day_str = start_of_day.strftime("%Y-%m-%d %H:%M:%S")
        end_of_day_str = end_of_day.strftime("%Y-%m-%d %H:%M:%S")
        
        todayDBquery =  {
                    "timestamp": {"$gte": start_of_day_str, "$lt": end_of_day_str}
                }
        
        print(f"todays query: {todayDBquery}")

        # Fetch today's data from the database
        today_data = list(
            db.sensor_data.find(
               todayDBquery
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
            trends.append({
                "timestamp": entry.get("timestamp"),
                "temperature": round(temperature, 1),
                "humidity": round(humidity, 1),
            })

        # Emit trends data to the client
        emit("today_trends_response", {"trends": trends})
    except Exception as e:
        print(f"Error handling today_trends_request: {e}")
        emit("today_trends_response", {"error": str(e)})



if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=9080)
