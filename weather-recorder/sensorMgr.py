import requests
import json
import Adafruit_DHT
from smbus2 import SMBus
import time
from datetime import datetime
import pytz 

# DHT22 Setup
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 'P8_11'

# API Endpoint
API_URL = "http://localhost:5000/data"

# Time Zone Setup
LOCAL_TIMEZONE = pytz.timezone("America/New_York")  # <------ Set to America/New_York

def get_localized_time():
    """Return the current time in the America/New_York timezone."""  
    return datetime.now(LOCAL_TIMEZONE)  

def read_sensors():
    # Read DHT22
    humidity, temperature_dht = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    # Get timestamp in localized timezone
    localized_timestamp = get_localized_time().strftime("%Y-%m-%d %H:%M:%S")  

    return {
        "temperature_dht": temperature_dht,
        "humidity": humidity,
        "timestamp": localized_timestamp  # <------ Use localized timestamp
    }

def send_data_to_api(data):
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code == 201:
            print("Data sent successfully.")
        else:
            print(f"Failed to send data: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

while True:
    sensor_data = read_sensors()
    print("Sensor Data:", sensor_data)
    send_data_to_api(sensor_data)
    time.sleep(10)  # Send data every 10 seconds
