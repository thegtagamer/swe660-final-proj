import json
import numpy as np
from flask import Flask, jsonify
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
import tensorflow.lite as tflite
from datetime import datetime, timedelta
import pytz  # For timezone handling

# Flask app setup
app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb+srv://adey6:7GvI8KrtEXfBQtvq@swe-project.n3gqd.mongodb.net/?retryWrites=true&w=majority&appName=SWE-project")
db = client.weather_db
forecast_collection = db.weather_forecast

# Timezone setup for New York
NY_TIMEZONE = pytz.timezone("America/New_York")

# Load the TFLite model
TFLITE_MODEL_PATH = "weather_transformer_model.tflite"
interpreter = tflite.Interpreter(model_path=TFLITE_MODEL_PATH)
interpreter.allocate_tensors()

# Get input and output tensor details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load scaler values
with open("scaler_values.json", "r") as f:
    scaler_values = json.load(f)

scaler_min = np.array(scaler_values["scaler_min"])
scaler_max = np.array(scaler_values["scaler_max"])

def scale_input(data):
    """Scales input using pre-determined min-max scaler."""
    return (data - scaler_min) / (scaler_max - scaler_min)

def predict_weather_and_temp(today_temp_max, today_temp_min):
    """Predict weather and temperature based on TFLite model."""
    default_wind = 0.5
    default_precipitation = 0.1
    temp_range = today_temp_max - today_temp_min
    day_of_week = datetime.now(NY_TIMEZONE).weekday()

    input_data = np.array([[today_temp_max, today_temp_min, default_wind, default_precipitation, temp_range, day_of_week]])
    input_data = scale_input(input_data).reshape((1, 1, input_data.shape[1])).astype(np.float32)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    weather_output = interpreter.get_tensor(output_details[0]['index'])
    predicted_weather_index = np.argmax(weather_output)

    weather_labels = ["sunny", "cloudy", "rainy", "snowy", "drizzle"]
    predicted_weather = weather_labels[predicted_weather_index]

    predicted_temperature = today_temp_max + 2  # Placeholder logic

    return predicted_weather, predicted_temperature

def fetch_today_min_max():
    """Fetches today's min and max temperatures from the database."""
    now = datetime.now(NY_TIMEZONE)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    query = {"timestamp": {"$gte": start_of_day.strftime("%Y-%m-%d %H:%M:%S"), "$lt": end_of_day.strftime("%Y-%m-%d %H:%M:%S")}}
    projection = {"temperature": 1, "_id": 0}

    records = list(db.sensor_data.find(query, projection))
    temperatures = [record["temperature"] for record in records if "temperature" in record]

    if not temperatures:
        return None, None

    return min(temperatures), max(temperatures)

def update_weather_forecast():
    """Updates the weather_forecast collection with predicted values."""
    today_temp_min, today_temp_max = fetch_today_min_max()
    if today_temp_min is None or today_temp_max is None:
        print("No temperature data available for today.")
        return

    predicted_weather, predicted_temperature = predict_weather_and_temp(today_temp_max, today_temp_min)

    forecast_data = {
        "timestamp": datetime.now(NY_TIMEZONE).strftime("%Y-%m-%d %H:%M:%S"),
        "predicted_weather": predicted_weather,
        "predicted_temperature": round(predicted_temperature, 1)
    }

    forecast_collection.insert_one(forecast_data)
    print("Weather forecast updated:", forecast_data)

@app.route("/forecast", methods=["GET"])
def get_forecast():
    """Fetches the latest forecast from the database."""
    latest_forecast = forecast_collection.find_one(sort=[("timestamp", -1)])
    if latest_forecast:
        return jsonify(latest_forecast), 200
    else:
        return jsonify({"message": "No forecast available."}), 404

# Schedule the forecast updates every 10 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(update_weather_forecast, 'interval', minutes=1)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9200)

