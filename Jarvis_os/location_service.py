# location_service.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENCAGE_KEY = os.getenv("OPENCAGE_API_KEY")


def geocode(place: str):
    """
    Convert place name → (formatted name, lat, lon)
    """
    try:
        url = "https://api.opencagedata.com/geocode/v1/json"
        res = requests.get(
            url,
            params={
                "q": place,
                "key": OPENCAGE_KEY,
                "limit": 1
            },
            timeout=5
        ).json()

        if not res.get("results"):
            return None

        result = res["results"][0]
        name = result["formatted"]
        lat = result["geometry"]["lat"]
        lon = result["geometry"]["lng"]

        return name, (lat, lon)

    except Exception:
        return None


def get_current_location():
    """
    Detect current city using IP (FREE)
    """
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        data = res.json()

        city = data.get("city")
        loc = data.get("loc")  # "lat,lon"

        if not city or not loc:
            return None, None

        lat, lon = loc.split(",")
        return city, (float(lat), float(lon))

    except Exception:
        return None, None
