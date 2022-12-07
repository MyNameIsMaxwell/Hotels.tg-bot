# -*- coding: utf-8 -*-
def low_high_price_payload(command, city_id, hotels_count, date_in, date_out):
	"""
	Функция, которая возвращает условия поиска в виде словаря для дальнейшей обработки requests.
    :param command: (str) название выбранной операции поиска.
    :param city_id: (str) id города, в котором пользователь ищет отели.
    :param hotels_count: (str) разыскиваемое количество отелей в городе.
    :param date_in: (date) дата въезда в отель.
    :param date_out: (date) дата выезда из отеля.
	:return: dict
	"""
	year_in, month_in, day_in = date_in.split("-")
	if day_in[0] == '0':
		day_in = day_in[1]
	year_out, month_out, day_out = date_out.split("-")
	if day_out[0] == '0':
		day_out = day_out[1]

	if command == "lowprice":
		lowprice_payload = {
			"currency": "USD",
			"locale": "ru_RU",
			"destination": {
				"regionId": city_id
			},
			"checkInDate": {
				"day": int(day_in),
				"month": int(month_in),
				"year": int(year_in)
			},
			"checkOutDate": {
				"day": int(day_out),
				"month": int(month_out),
				"year": int(year_out)
			},
			"rooms": [
				{
					"adults": 1
				}
			],
			"resultsStartingIndex": 0,
			"resultsSize": int(hotels_count),
			"sort": "PRICE_LOW_TO_HIGH"
		}
		return lowprice_payload
	else:
		highprice_payload = {
			"currency": "USD",
			"locale": "ru_RU",
			"destination": {
				"regionId": city_id
			},
			"checkInDate": {
				"day": int(day_in),
				"month": int(month_in),
				"year": int(year_in)
			},
			"checkOutDate": {
				"day": int(day_out),
				"month": int(month_out),
				"year": int(year_out)
			},
			"rooms": [
				{
					"adults": 1
				}
			],
			"resultsStartingIndex": 0,
			"resultsSize": int(hotels_count),
			"sort": "PRICE_HIGH_TO_LOW"
		}
		return highprice_payload


def bestdeal_payload(city_id, hotels_count, price, date_in, date_out):
	year_in, month_in, day_in = date_in.split("-")
	if day_in[0] == '0':
		day_in = day_in[1]
	year_out, month_out, day_out = date_out.split("-")
	if day_out[0] == '0':
		day_out = day_out[1]

	best_payload = {
		"currency": "USD",
		"locale": "ru_RU",
		"destination": {
			"regionId": city_id
		},
		"checkInDate": {
			"day": int(day_in),
			"month": int(month_in),
			"year": int(year_in)
		},
		"checkOutDate": {
			"day": int(day_out),
			"month": int(month_out),
			"year": int(year_out)
		},
		"rooms": [
			{
				"adults": 1
			}
		],
		"resultsStartingIndex": 0,
		"resultsSize": 50,
		"sort": "DISTANCE",
		"filters": {
			"price": {
				"max": price,
				"min": 1
			}
		}
	}
	return best_payload
