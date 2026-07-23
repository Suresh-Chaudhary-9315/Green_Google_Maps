import requests
from config import API_KEY


# ---------------------------
# Get Coordinates
# ---------------------------
def get_coordinates(address):

    url = f"https://api.tomtom.com/search/2/geocode/{address}.json"

    params = {
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    data = response.json()

    if data["results"]:
        lat = data["results"][0]["position"]["lat"]
        lon = data["results"][0]["position"]["lon"]
        return lat, lon

    return None


# ---------------------------
# Get Route(s)
# ---------------------------
def get_route(source_lat, source_lon, dest_lat, dest_lon, max_alternatives=2):

    url = (
        f"https://api.tomtom.com/routing/1/calculateRoute/"
        f"{source_lat},{source_lon}:{dest_lat},{dest_lon}/json"
    )

    params = {
        "key": API_KEY,
        "traffic": "true",
        "computeTravelTimeFor": "all",
        "maxAlternatives": max(0, max_alternatives - 1),
        # make sure TomTom sends back the actual road geometry, not just the summary
        "routeRepresentation": "polyline",
    }

    response = requests.get(url, params=params)

    data = response.json()

    if "routes" not in data:
        return None

    routes = []
    for route in data["routes"]:
        summary = route["summary"]

        # Pull the lat/lon points for every leg so the route can be drawn
        # on a map exactly like it would appear on Google Maps.
        geometry = []
        for leg in route.get("legs", []):
            for point in leg.get("points", []):
                geometry.append((point["latitude"], point["longitude"]))

        routes.append({
            "distance_km": summary["lengthInMeters"] / 1000,
            "travel_time_min": summary["travelTimeInSeconds"] / 60,
            "traffic_delay_min": summary["trafficDelayInSeconds"] / 60,
            "geometry": geometry,
        })

    return routes