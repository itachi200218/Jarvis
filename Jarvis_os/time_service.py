import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from location_service import geocode

load_dotenv()

TIMEZONEDB_KEY = os.getenv("TIMEZONEDB_API_KEY")

def get_time_from_timezone_db(place: str) -> str:
    try:
        note = geocode(place)
        if not note:
            return f"I couldn't find the time for {place}."

        name, (lat, lon) = note

        res = requests.get(
            "http://api.timezonedb.com/v2.1/get-time-zone",
            params={
                "key": TIMEZONEDB_KEY,
                "format": "json",
                "by": "position",
                "lat": lat,
                "lng": lon
            },
            timeout=5
        ).json()

        if res["status"] != "OK":
            return "I couldn't fetch the time right now."

        local_time = datetime.utcfromtimestamp(res["timestamp"])

        return f"The current time in {name} is {local_time.strftime('%H:%M')}."

    except Exception:
        return "I was unable to get the time right now."
