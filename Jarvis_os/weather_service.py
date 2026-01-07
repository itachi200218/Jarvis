# weather_service.py
import requests


def get_weather(city: str) -> str:
    """
    Fetch current weather using Open-Meteo (no API key)
    """
    try:
        # Step 1: Convert city → latitude & longitude
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_res = requests.get(geo_url, params=geo_params, timeout=5)
        geo_data = geo_res.json()

        if "results" not in geo_data:
            return f"I couldn't find weather data for {city}."

        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]

        # Step 2: Get current weather
        weather_url = "https://api.open-meteo.com/v1/forecast"
        weather_params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True
        }

        weather_res = requests.get(weather_url, params=weather_params, timeout=5)
        weather_data = weather_res.json()

        current = weather_data.get("current_weather")
        if not current:
            return "Weather data is unavailable right now."

        temp = current["temperature"]
        wind = current["windspeed"]
        code = current["weathercode"]

        return (
            f"The current temperature in {city} is {temp}°C "
            f"with wind speed {wind} kilometers per hour."
        )

    except Exception:
        return "I was unable to fetch the weather right now."
