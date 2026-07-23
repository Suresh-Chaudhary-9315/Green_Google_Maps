import joblib
import pandas as pd

model = joblib.load("co2_model.pkl")
vehicle_encoder = joblib.load("vehicle_encoder.pkl")
fuel_encoder = joblib.load("fuel_encoder.pkl")

FEATURE_COLUMNS = [
    "Distance_km", "Travel_Time_min", "Avg_Speed_kmh",
    "Traffic_Level", "Vehicle_Type", "Fuel_Type",
]

TRAFFIC_LEVEL_MAP = {"Low": 0, "Moderate": 1, "High": 2, "Severe": 3}

MIN_CO2_PER_KM = 0.10
MAX_CO2_PER_KM = 0.45


# ---------- Derived route stats ----------

def calculate_avg_speed(distance_km, travel_time_min):
    if travel_time_min <= 0:
        return 0.0
    return distance_km / (travel_time_min / 60)


def estimate_traffic_level(travel_time_min, traffic_delay_min):
    no_traffic_min = travel_time_min - traffic_delay_min
    if no_traffic_min <= 0:
        return "Low"

    ratio = traffic_delay_min / no_traffic_min
    if ratio < 0.1:
        return "Low"
    if ratio < 0.3:
        return "Moderate"
    if ratio < 0.6:
        return "High"
    return "Severe"


# ---------- Encoding + prediction ----------

def build_feature_vector(distance_km, travel_time_min, avg_speed_kmh,
                          traffic_level, vehicle_type, fuel_type):
    features = [[
        distance_km,
        travel_time_min,
        avg_speed_kmh,
        TRAFFIC_LEVEL_MAP[traffic_level],
        vehicle_encoder.transform([vehicle_type])[0],
        fuel_encoder.transform([fuel_type])[0],
    ]]
    return pd.DataFrame(features, columns=FEATURE_COLUMNS)


def predict_co2_emission(distance_km, travel_time_min, avg_speed_kmh,
                          traffic_level, vehicle_type, fuel_type):
    features = build_feature_vector(
        distance_km, travel_time_min, avg_speed_kmh,
        traffic_level, vehicle_type, fuel_type,
    )
    return float(model.predict(features)[0])


# ---------- Eco score + rating ----------

def compute_eco_score(co2_kg, distance_km):
    if distance_km <= 0:
        return 0.0

    co2_per_km = co2_kg / distance_km
    co2_per_km = max(MIN_CO2_PER_KM, min(MAX_CO2_PER_KM, co2_per_km))
    normalized = (co2_per_km - MIN_CO2_PER_KM) / (MAX_CO2_PER_KM - MIN_CO2_PER_KM)

    return round((1 - normalized) * 100, 1)


def rate_route(eco_score):
    if eco_score >= 80:
        return "Excellent"
    if eco_score >= 60:
        return "Good"
    if eco_score >= 40:
        return "Moderate"
    if eco_score >= 20:
        return "Poor"
    return "Very Poor"


# ---------- Score a route dict coming from api.get_route() ----------

def score_route(route, vehicle_type, fuel_type):
    """
    route: dict from api.get_route() -> {distance_km, travel_time_min, traffic_delay_min}
    Adds avg_speed_kmh, traffic_level, predicted_co2_kg, eco_score, rating.
    """
    avg_speed_kmh = calculate_avg_speed(route["distance_km"], route["travel_time_min"])
    traffic_level = estimate_traffic_level(route["travel_time_min"], route["traffic_delay_min"])

    co2_kg = predict_co2_emission(
        route["distance_km"], route["travel_time_min"], avg_speed_kmh,
        traffic_level, vehicle_type, fuel_type,
    )
    eco_score = compute_eco_score(co2_kg, route["distance_km"])

    return {
        **route,
        "avg_speed_kmh": round(avg_speed_kmh, 2),
        "traffic_level": traffic_level,
        "predicted_co2_kg": round(co2_kg, 3),
        "eco_score": eco_score,
        "rating": rate_route(eco_score),
    }


def recommend_green_route(routes, vehicle_type, fuel_type):
    """
    routes: list of dicts, each from api.get_route()
    Scores every route, tags each with a relative_label, and returns the
    one with the highest eco_score as "recommended".
    """
    scored_routes = [score_route(r, vehicle_type, fuel_type) for r in routes]

    best_index = max(range(len(scored_routes)), key=lambda i: scored_routes[i]["eco_score"])
    best_score = scored_routes[best_index]["eco_score"]

    for i, route in enumerate(scored_routes):
        if i == best_index:
            route["relative_label"] = "Greenest of your options"
        else:
            diff = round(best_score - route["eco_score"], 1)
            if diff == 0:
                route["relative_label"] = "Same eco score as the greenest option"
            else:
                route["relative_label"] = f"{diff} points more CO2-intensive than the greenest option"

    best_route = scored_routes[best_index]
    return {"routes": scored_routes, "recommended": best_route}