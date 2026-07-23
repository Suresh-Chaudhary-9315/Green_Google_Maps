from api import get_coordinates, get_route

src = get_coordinates("Connaught Place, Delhi")
dst = get_coordinates("India Gate, Delhi")
print("Source:", src)
print("Destination:", dst)

routes = get_route(src[0], src[1], dst[0], dst[1])
print("Routes found:", len(routes))
for r in routes:
    print(r)
from utils import recommend_green_route

result = recommend_green_route(routes, vehicle_type="Sedan", fuel_type="Petrol")
print(result["recommended"])