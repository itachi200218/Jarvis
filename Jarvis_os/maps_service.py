# maps_service.py
import requests
from location_service import get_current_location


def get_distance(source: str | None, destination: str) -> str:
    try:
        # =========================
        # 1️⃣ Resolve source
        # =========================
        if source is None:
            current_city, current_coords = get_current_location()
            if not current_coords:
                return "I couldn't detect your current location."
            source_city = current_city
            source_lat, source_lon = current_coords
        else:
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_params = {
                "name": source,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            geo_res = requests.get(geo_url, params=geo_params, timeout=5)
            geo_data = geo_res.json()

            if not geo_data.get("results"):
                return f"I couldn't find {source} on the map."

            loc = geo_data["results"][0]
            source_city = loc["name"]
            source_lat = loc["latitude"]
            source_lon = loc["longitude"]

        # =========================
        # 2️⃣ Resolve destination
        # =========================
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": destination,
            "count": 1,
            "language": "en",
            "format": "json"
        }
        geo_res = requests.get(geo_url, params=geo_params, timeout=5)
        geo_data = geo_res.json()

        if not geo_data.get("results"):
            return f"I couldn't find {destination} on the map."

        dest = geo_data["results"][0]
        dest_city = dest["name"]
        dest_lat = dest["latitude"]
        dest_lon = dest["longitude"]

        # =========================
        # 3️⃣ Route via OSRM
        # =========================
        route_url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{source_lon},{source_lat};{dest_lon},{dest_lat}"
        )

        route_res = requests.get(route_url, timeout=5)
        route_data = route_res.json()

        route = route_data["routes"][0]
        distance_km = round(route["distance"] / 1000, 2)
        duration_min = round(route["duration"] / 60)

        return (
            f"The distance from {source_city} to {dest_city} is about "
            f"{distance_km} kilometers. Estimated travel time is {duration_min} minutes."
        )

    except Exception:
        return "I was unable to calculate the distance right now."
