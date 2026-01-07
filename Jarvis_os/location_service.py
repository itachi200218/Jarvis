# location_service.py
import requests


def get_current_location():
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
