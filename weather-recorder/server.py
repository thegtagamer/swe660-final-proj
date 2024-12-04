from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://adey6:7GvI8KrtEXfBQtvq@swe-project.n3gqd.mongodb.net/?retryWrites=true&w=majority&appName=SWE-project")

db = client.weather_db
collection = db.sensor_data

@app.route('/data', methods=['POST'])
def save_data():
    try:
        data = request.json  # Read incoming JSON data
        if not data:
            return jsonify({"error": "No data provided"}), 400
        collection.insert_one(data)  # Write data to MongoDB
        return jsonify({"message": "Data saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)  # Expose API on port 9000

