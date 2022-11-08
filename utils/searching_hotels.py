import requests
import json


from config_data import config


def hotel_in_city_info(city):
	url = "https://hotels4.p.rapidapi.com/locations/v3/search"
	querystring = {"q": f"{city}", "locale": "ru_RU", "langid": "1033", "siteid": "300000001"}

	hotels_api = requests.request("GET", url, headers=config.headers, params=querystring, timeout=10)
	if hotels_api.status_code == 200:
		json_dict = json.loads(hotels_api.text)

		# with open("test.json", 'w', encoding='utf-8') as file:
		# 	json.dump(json_dict, file, indent=4, ensure_ascii=False)
# def city_destination_id(city):
#     url = "https://hotels4.p.rapidapi.com/locations/v2/search"
#     querystring = {"query": city}
#     response = requests.request("GET", url, headers=headers, params=querystring)
#
#     try:
#         return response.json()["suggestions"][0]["entities"][0]["destinationId"]
#     except:
#         return None
