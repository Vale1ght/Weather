import os
import requests
from datetime import datetime
from dotenv import load_dotenv


class WeatherAPI(object):
    def __init__(self):
        dotenv_path = os.path.join("config", ".env")
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
        self.api_key = os.getenv("API_KEY")

    def get_city_coordinates(self, city: str) -> tuple:
        try:
            response = requests.get(
                f"https://api.openweathermap.org/geo/1.0/direct",
                params={
                    "q": city,
                    "limit": 1,
                    "appid": self.api_key,
                }
            )
            response.raise_for_status()
            data = response.json()

            if data:
                return data[0]["lat"], data[0]["lon"]
            else:
                raise ValueError("City not found")

        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None, None

    def get_weather(self, city: str) -> dict:
        city_coordinates = self.get_city_coordinates(city)
        if city_coordinates:
            lat, lon = city_coordinates
        else:
            return print("City not found, please try another city.")

        try:
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "units": "metric",
                    "appid": self.api_key,
                }
            )
            response.raise_for_status()
            data = response.json()

            return {
                "city": data["name"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
            }

        except requests.RequestException as e:
            print(f"API Error: {e}")
            return {}

    def get_hourly_forecast(self, city: str) -> dict:
        city_coordinates = self.get_city_coordinates(city)
        if city_coordinates:
            lat, lon = city_coordinates
        else:
            return print("City not found, please try another city.")

        try:
            response = requests.get(
                f"https://pro.openweathermap.org/data/2.5/forecast/hourly",
                params={
                    "lat": lat,
                    "lon": lon,
                    "cnt": 24,
                    "units": "metric",
                    "appid": self.api_key,
                }
            )
            response.raise_for_status()
            data = response.json()

            forecast_list = []
            for item in data["list"]:
                forecast_list.append({
                    "datetime": datetime.fromtimestamp(item["dt"]).strftime('%H:%M'),
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "description": item["weather"][0]["description"],
                    "wind_speed": item["wind"]["speed"],
                    "humidity": item["main"]["humidity"]
                })

            return forecast_list

        except requests.RequestException as e:
            print(f"API Error: {e}")
            return []

    def get_weekly_forecast(self, city: str) -> dict:
        city_coordinates = self.get_city_coordinates(city)
        if city_coordinates:
            lat, lon = city_coordinates
        else:
            return print("City not found, please try another city.")

        try:
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast/daily",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "cnt": 7,
                    "units": "metric",
                }
            )
            response.raise_for_status()
            data = response.json()

            weekly_forecast_list = []
            for day in data["list"]:
                description = day["weather"][0]["description"]
                weekly_forecast_list.append({
                    "day": datetime.fromtimestamp(day["dt"]).strftime("%A"),
                    "temperature_day": day["temp"]["max"],
                    "temperature_night": day["temp"]["min"],
                    "description": description,
                })

            return weekly_forecast_list

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return {}
