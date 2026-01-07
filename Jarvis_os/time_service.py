# time_service.py
import requests
from datetime import datetime, timedelta


def geocode_place(query: str):
    """Try multiple geocoding strategies"""
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"

    attempts = [
        query,                          # "india kolkata"
        " ".join(query.split()[::-1]),  # "kolkata india"
        query.split()[-1]               # "kolkata"
    ]

    for q in attempts:
        res = requests.get(
            geo_url,
            params={
                "name": q,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=5
        )

        data = res.json()
        if data.get("results"):
            return data["results"][0]

    return None


def get_time_from_timezone_db(spoken_location: str) -> str:
    try:
        # ==============================
        # 1️⃣ Geocode place (SMART)
        # ==============================
        location = geocode_place(spoken_location)

        if not location:
            return f"I couldn't find the time for {spoken_location}."

        lat = location["latitude"]
        lon = location["longitude"]
        city = location["name"]
        country = location.get("country", "")

        # ==============================
        # 2️⃣ Get timezone info (AUTO)
        # ==============================
        time_res = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "timezone": "auto"
            },
            timeout=5
        )

        time_data = time_res.json()
        utc_offset = time_data.get("utc_offset_seconds")

        if utc_offset is None:
            return "I couldn't fetch the time right now."

        # ==============================
        # 3️⃣ Calculate REAL local time
        # ==============================
        local_time = datetime.utcnow() + timedelta(seconds=utc_offset)
        time_str = local_time.strftime("%H:%M")

        place = f"{city}, {country}" if country else city
        return f"The current time in {place} is {time_str}."

    except Exception:
        return "I was unable to get the time right now."
