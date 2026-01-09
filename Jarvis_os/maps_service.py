from location_service import geocode, get_current_location
from nlp_utils import extract_places

def get_distance(query_or_source, destination=None) -> str:
    try:
        # 🔥 Natural language mode
        if destination is None:
            source, destination = extract_places(query_or_source)
        else:
            source = query_or_source

        if not destination:
            return "Please tell me the destination."

        # 🔥 Handle 'my location'
        if source in (None, "", "my location", "current location", "here"):
            current = get_current_location()
            if not current or not current[1]:
                return "I couldn't detect your current location."
            source_name, source_coords = current
        else:
            src = geocode(source)
            if not src:
                return f"I couldn't find {source}."
            source_name, source_coords = src

        dst = geocode(destination)
        if not dst:
            return f"I couldn't find {destination}."

        dest_name, dest_coords = dst

        # OpenRouteService
        res = requests.get(
            "https://api.openrouteservice.org/v2/directions/driving-car",
            params={
                "api_key": ORS_KEY,
                "start": f"{source_coords[1]},{source_coords[0]}",
                "end": f"{dest_coords[1]},{dest_coords[0]}"
            },
            timeout=5
        ).json()

        route = res["features"][0]["properties"]["summary"]
        km = round(route["distance"] / 1000, 2)
        mins = round(route["duration"] / 60)

        return (
            f"The distance from {source_name} to {dest_name} "
            f"is about {km} kilometers. "
            f"Estimated travel time is {mins} minutes."
        )

    except Exception:
        return "I was unable to calculate the distance right now."
