from geopy.distance import geodesic


def distance_from_center(city_coord, hotel_coord):
	# city_coord = (41.49008, -71.312796)
	# hotel_coord = (41.499498, -81.695391)
	distance_from_center = int(geodesic(city_coord, hotel_coord).m)
	return distance_from_center
