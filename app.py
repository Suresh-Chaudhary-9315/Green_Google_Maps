import streamlit as st
import folium
from streamlit_folium import st_folium

from api import get_coordinates, get_route
from utils import recommend_green_route

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Green Route Finder",
    page_icon="🌿",
    layout="wide",
)

VEHICLE_TYPES = ["Hatchback", "Motorcycle", "SUV", "Sedan"]
FUEL_TYPES = ["Diesel", "Petrol"]

RATING_COLORS = {
    "Excellent": "#1e8f4e",
    "Good": "#7ac043",
    "Moderate": "#f2b705",
    "Poor": "#f2811d",
    "Very Poor": "#d9342b",
}

# Distinct colors for each route line, in the order routes come back from TomTom.
ROUTE_LINE_COLORS = ["#3388ff", "#9b59b6", "#e67e22", "#16a085", "#c0392b"]

if "result" not in st.session_state:
    st.session_state.result = None


# ---------------------------------------------------------------------------
# Sidebar — trip inputs
# ---------------------------------------------------------------------------
st.sidebar.title("🌿 Green Route Finder")
st.sidebar.caption("Find the most eco-friendly way to get there.")

source_address = st.sidebar.text_input("Start address", placeholder="e.g. Connaught Place, Delhi")
dest_address = st.sidebar.text_input("Destination address", placeholder="e.g. India Gate, Delhi")

vehicle_type = st.sidebar.selectbox("Vehicle type", VEHICLE_TYPES)
fuel_type = st.sidebar.selectbox("Fuel type", FUEL_TYPES)

max_alternatives = st.sidebar.slider("Number of route options", min_value=1, max_value=4, value=3)

find_clicked = st.sidebar.button("Find green route", type="primary", use_container_width=True)

st.sidebar.divider()
st.sidebar.markdown(
    "**Rating scale**\n\n"
    + "\n".join(f"- <span style='color:{c}'>●</span> {r}" for r, c in RATING_COLORS.items()),
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Fetch + score routes
# ---------------------------------------------------------------------------
if find_clicked:
    if not source_address or not dest_address:
        st.sidebar.error("Please enter both a start and a destination address.")
    else:
        with st.spinner("Geocoding addresses..."):
            source_coords = get_coordinates(source_address)
            dest_coords = get_coordinates(dest_address)

        if not source_coords:
            st.sidebar.error(f"Couldn't find location: {source_address}")
        elif not dest_coords:
            st.sidebar.error(f"Couldn't find location: {dest_address}")
        else:
            with st.spinner("Fetching routes from TomTom..."):
                routes = get_route(
                    source_coords[0], source_coords[1],
                    dest_coords[0], dest_coords[1],
                    max_alternatives=max_alternatives,
                )

            if not routes:
                st.sidebar.error("No routes found between these locations.")
            else:
                with st.spinner("Scoring routes for CO2 emissions..."):
                    scored = recommend_green_route(routes, vehicle_type, fuel_type)

                st.session_state.result = {
                    "source_coords": source_coords,
                    "dest_coords": dest_coords,
                    "source_address": source_address,
                    "dest_address": dest_address,
                    "scored": scored,
                }


# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------
st.title("Green Google Maps 🌍")
st.caption("Compare routes not just by time and distance, but by their carbon footprint.")

result = st.session_state.result

if result is None:
    st.info("Enter a start and destination address in the sidebar, then click **Find green route**.")
else:
    scored = result["scored"]
    routes = scored["routes"]
    recommended = scored["recommended"]
    source_coords = result["source_coords"]
    dest_coords = result["dest_coords"]

    map_col, info_col = st.columns([2.2, 1])

    # -----------------------------------------------------------------
    # Map
    # -----------------------------------------------------------------
    with map_col:
        mid_lat = (source_coords[0] + dest_coords[0]) / 2
        mid_lon = (source_coords[1] + dest_coords[1]) / 2

        fmap = folium.Map(location=[mid_lat, mid_lon], zoom_start=13, tiles="cartodbpositron")

        folium.Marker(
            location=source_coords,
            tooltip=f"Start: {result['source_address']}",
            icon=folium.Icon(color="blue", icon="play", prefix="fa"),
        ).add_to(fmap)

        folium.Marker(
            location=dest_coords,
            tooltip=f"Destination: {result['dest_address']}",
            icon=folium.Icon(color="red", icon="flag-checkered", prefix="fa"),
        ).add_to(fmap)

        bounds = [source_coords, dest_coords]

        for i, route in enumerate(routes):
            is_best = route is recommended
            geometry = route.get("geometry") or [source_coords, dest_coords]
            bounds.extend(geometry)

            folium.PolyLine(
                locations=geometry,
                color="#1e8f4e" if is_best else ROUTE_LINE_COLORS[i % len(ROUTE_LINE_COLORS)],
                weight=7 if is_best else 4,
                opacity=0.95 if is_best else 0.55,
                dash_array=None if is_best else "6,6",
                tooltip=(
                    f"{'🌿 Greenest route' if is_best else f'Route {i + 1}'} — "
                    f"{route['distance_km']:.1f} km, {route['travel_time_min']:.0f} min, "
                    f"eco score {route['eco_score']}"
                ),
            ).add_to(fmap)

        fmap.fit_bounds(bounds)

        st_folium(fmap, width=None, height=560, returned_objects=[])

    # -----------------------------------------------------------------
    # Route comparison cards
    # -----------------------------------------------------------------
    with info_col:
        st.subheader("Route options")

        sorted_routes = sorted(routes, key=lambda r: r["eco_score"], reverse=True)

        for i, route in enumerate(sorted_routes):
            is_best = route is recommended
            color = RATING_COLORS.get(route["rating"], "#888888")

            with st.container(border=True):
                header = "🌿 Recommended" if is_best else f"Route option {i + 1}"
                st.markdown(f"**{header}**")

                st.markdown(
                    f"<span style='background-color:{color};color:white;"
                    f"padding:2px 8px;border-radius:10px;font-size:0.8em'>"
                    f"{route['rating']} · eco score {route['eco_score']}</span>",
                    unsafe_allow_html=True,
                )

                c1, c2, c3 = st.columns(3)
                c1.metric("Distance", f"{route['distance_km']:.1f} km")
                c2.metric("Time", f"{route['travel_time_min']:.0f} min")
                c3.metric("CO₂", f"{route['predicted_co2_kg']:.2f} kg")

                st.caption(
                    f"Traffic: {route['traffic_level']} · "
                    f"Avg speed: {route['avg_speed_kmh']:.0f} km/h · "
                    f"Delay: {route['traffic_delay_min']:.0f} min"
                )
                st.caption(route["relative_label"])

    st.divider()
    st.caption(
        f"Vehicle: {vehicle_type} ({fuel_type}) · "
        f"Model: Random Forest Regressor · Routing: TomTom Routing API"
    )