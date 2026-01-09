# weather_service.py
import os
import re
import requests
from dotenv import load_dotenv
from rapidfuzz import process, fuzz

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")

# Known cities for fuzzy correction (expand anytime)
KNOWN_CITIES = [
    "Hyderabad", "Bangalore", "Chennai", "Delhi", "Mumbai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Noida",
    "Gurgaon", "Coimbatore", "Vijayawada", "Warangal",
    "Los Angeles", "New York", "San Francisco",
    "Tokyo", "Osaka", "Kyoto",
    "London", "Paris", "Berlin"
]

# Country hints mapping
COUNTRY_HINTS = {
    "usa": "USA",
    "united states": "USA",
    "america": "USA",
    "india": "India",
    "japan": "Japan",
    "uk": "UK",
    "england": "UK"
}


def normalize_city(city: str) -> str:
    """
    Fuzzy-correct city spelling
    """
    match, score, _ = process.extractOne(
        city,
        KNOWN_CITIES,
        scorer=fuzz.ratio
    )
    return match if score >= 70 else city


def extract_city_and_country(text: str):
    """
    Extract city + country from free text
    Example:
      'weather in los angles usa right now'
      → ('Los Angles', 'USA')
    """
    text = text.lower()

    country = None
    for key, value in COUNTRY_HINTS.items():
        if key in text:
            country = value
            text = text.replace(key, "")

    # Remove filler words
    text = re.sub(
        r"(weather|temperature|in|right now|today|now|tell me|what is)",
        "",
        text
    )

    city = text.strip()
    return city.title(), country


def get_weather(query: str) -> str:
    """
    Fetch accurate current weather using WeatherAPI (API key required)
    """
    try:
        if not API_KEY:
            return "Weather service is not configured."

        if not query or not query.strip():
            return "Please tell me a city name."

        # 🔥 Extract city & country from user query
        city, country = extract_city_and_country(query)

        if not city:
            return "Please tell me a city name."

        # 🔥 Fuzzy city correction
        city = normalize_city(city)

        # 🔥 Build WeatherAPI query
        location_query = city
        if country:
            location_query = f"{city}, {country}"

        url = "https://api.weatherapi.com/v1/current.json"
        params = {
            "key": API_KEY,
            "q": location_query,
            "aqi": "no"
        }

        res = requests.get(url, params=params, timeout=5)
        data = res.json()

        if "error" in data:
            return f"I couldn't find weather data for {city}."

        location = data["location"]
        current = data["current"]

        return (
            f"The current weather in {location['name']}, {location['country']} "
            f"is {current['condition']['text']}. "
            f"The temperature is {current['temp_c']}°C, "
            f"feels like {current['feelslike_c']}°C, "
            f"humidity {current['humidity']} percent, "
            f"with wind speed {current['wind_kph']} kilometers per hour."
        )

    except Exception:
        return "I was unable to fetch the weather right now."
