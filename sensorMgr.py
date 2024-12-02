import requests
import json
import Adafruit_DHT
from smbus2 import SMBus
import time

# DHT22 Setup
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 'P8_11'

# BMP180 Setup
# BMP180_ADDR = 0x77
# bus = SMBus(1)

# API Endpoint
API_URL = "http://localhost:5000/data"

def read_sensors():
    # Read DHT22
    humidity, temperature_dht = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    # Read BMP180
    # bus.write_byte_data(BMP180_ADDR, 0xF4, 0x2E)
    # time.sleep(0.05)
    # msb = bus.read_byte_data(BMP180_ADDR, 0xF6)
    # lsb = bus.read_byte_data(BMP180_ADDR, 0xF7)
    # temperature_bmp = ((msb << 8) + lsb) / 10.0

    return {
        "temperature_dht": temperature_dht,
        "humidity": humidity,
        # "temperature_bmp": temperature_bmp,
        "timestamp": time.time()  # Add current timestamp of data collection as per bb environment
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

