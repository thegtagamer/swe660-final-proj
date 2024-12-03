import json
import random
from datetime import datetime, timedelta

# Function to generate random weather data
# Function to generate random weather data
def generate_weather_data(start_date, end_date, locations):
    data = []
    current_date = start_date

    while current_date <= end_date:
        for location in locations:
            temperature = round(random.uniform(-10, 40), 2)  # Temperature range in °C
            feels_like = round(temperature + random.uniform(-3, 3), 2)
            humidity = random.randint(20, 90)  # Humidity percentage
            wind_speed = round(random.uniform(0, 30), 2)  # Wind speed in km/h
            precipitation = round(random.uniform(0, 20), 2)  # Precipitation in mm

            data.append({
                "timestamp": current_date.strftime("%Y-%m-%d %H:%M:%S"),  # DHT sensor format
                "temperature": temperature,
                "feels_like": feels_like,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "precipitation": precipitation,
                "location": location
            })

        current_date += timedelta(hours=1)  # Generate data hourly

    return data
# Define parameters
start_date = datetime.now() - timedelta(days=365)  # Start 1 year ago
end_date = datetime.now()  # Up to the current moment
locations = ["Fairfax", "New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]

# Generate dataset
dataset = generate_weather_data(start_date, end_date, locations)

# Write dataset to a JSON file
with open("weather_data.json", "w") as file:
    json.dump(dataset, file, indent=4)

print(f"Generated {len(dataset)} records of weather data.")

