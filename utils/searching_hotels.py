import re
import requests
from telebot.types import InputMediaPhoto
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import api_headers

def get_result_with_photos(hotel_id_value, hotels_photo_count, text):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(hotel_id_value)}

    response = requests.get(url, headers=api_headers, params=querystring)

    if response and response.text != '':
        result = list()
        photo_hotel_get = response.json()['hotelImages']
        # photo_room_get = response.json()['roomImages'][0]['images']
        for photo in photo_hotel_get:
            try:
                photo_url = photo['baseUrl']
                photo_size = [size['suffix'] for size in photo['sizes'] if size['suffix'] in ["z", "y"]][0]
                result.append(photo_url.format(size=photo_size))
            except Exception as exp:
                result = None
        if len(result) >= hotels_photo_count:
            photos_urls = result[:hotels_photo_count]
            photo_mosaic = [InputMediaPhoto(media=url, caption=text) if index == 0
                            else InputMediaPhoto(media=url) for index, url in enumerate(photos_urls)]
            return photo_mosaic, photos_urls
    else:
        return None


def get_hotels_info(command, city_id, hotels_count, date_in, date_out, photo_count=0):
    url = "https://hotels4.p.rapidapi.com/properties/list"
    if command == "lowprice":
        querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": str(hotels_count), "checkIn": str(date_in),
                   "checkOut": str(date_out), "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}
    elif command == "highprice":
        querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": str(hotels_count), "checkIn": str(date_in),
                       "checkOut": str(date_out), "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "ru_RU", "currency": "RUB"}
    response = requests.get(url, headers=api_headers, params=querystring)
    for hotel_id_value in response.json()["data"]["body"]["searchResults"]["results"]:
        try:
            hotel_id = hotel_id_value["id"]
            hotel_name = hotel_id_value["name"]
            hotel_address = hotel_id_value["address"]["streetAddress"]
            distance_from_center = hotel_id_value["landmarks"][0]["distance"]
            days = date_out - date_in
            price_one_day = hotel_id_value["ratePlan"]["price"]["current"]
            num = re.findall(r'\d+', price_one_day)
            sum_price = days.days * int(num[0] + num[1])
            all_days_price = re.sub(r'(?<=\d)(?=(\d{3})+\b)', ',', str(sum_price)) + price_one_day[-4:]
            hotel_url = 'https://www.hotels.com/ho' + str(hotel_id) + '/'
            msg = (f"<b>Отель: {hotel_name}\n"
                   f"Адрес: {hotel_address}\n"
                   f"Расстояние до центра: {distance_from_center}\n"
                   f"Цена за 1 сутки: {price_one_day}\n"
                   f"Стоимость за {days.days} суток: {all_days_price}\n"
                   f"Подробнее об отеле: {hotel_url}\n</b>")
            if int(photo_count) > 0:
                text = msg.replace("<b>", '').replace("</b>", '')
                result, photos = get_result_with_photos(hotel_id, photo_count, text)
                yield result, photos, [text]
            else:
                yield [msg]
        except KeyError:
            pass


def get_hotels_info_bestdeal(city_id, hotels_count, date_in, date_out,
                             distance, price, photo_count=0, command="bestdeal"):
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": "25", "checkIn": str(date_in),
                   "checkOut": str(date_out), "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}

    response = requests.get(url, headers=api_headers, params=querystring)

    hotels_counter = 0

    for hotel_id_value in response.json()["data"]["body"]["searchResults"]["results"]:
       try:
            if hotels_counter == int(hotels_count):
                break
            hotel_id = hotel_id_value["id"]
            hotel_name = hotel_id_value["name"]
            hotel_address = hotel_id_value["address"]["streetAddress"]
            distance_from_center = hotel_id_value["landmarks"][0]["distance"]
            days = date_out - date_in
            price_one_day = hotel_id_value["ratePlan"]["price"]["current"]
            num = re.findall(r'\d+', price_one_day)
            sum_price = days.days * int(num[0] + num[1])
            all_days_price = re.sub(r'(?<=\d)(?=(\d{3})+\b)', ',', str(sum_price)) + price_one_day[-4:]
            hotel_url = 'https://www.hotels.com/ho' + str(hotel_id) + '/'
            if not int(num[0] + num[1]) >= int(price) and not float(distance_from_center[:-3].replace(',', '.')) >= float(distance):

                msg = (f"<b>Отель: {hotel_name}\n"
                       f"Адрес: {hotel_address}\n"
                       f"Расстояние до центра: {distance_from_center}\n"
                       f"Цена за 1 сутки: {price_one_day}\n"
                       f"Стоимость за {days.days} суток: {all_days_price}\n"
                       f"Подробнее об отеле: {hotel_url}\n</b>")

                if int(photo_count) > 0:
                    hotels_counter += 1
                    text = msg.replace("<b>", '').replace("</b>", '')
                    result, photos = get_result_with_photos(hotel_id, photo_count, text)
                    yield result, photos, [text]
                else:
                    hotels_counter += 1
                    yield [msg]
       except Exception as exp:
           pass
    if photo_count == 0 and hotels_counter == 0:
        return ["Отелей с таким запросом не найдено😔"]


def get_city_name_and_id(city):
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city, "locale": "ru_RU", "currency": "USD"}
    hotels_api = requests.get(url, headers=api_headers, params=querystring)
    if hotels_api.status_code == 200:
        cities = list()
        try:
            for elem in hotels_api.json()["suggestions"][0]["entities"]:
                if elem["type"] == "CITY":
                    pattern = r'\<(/?[^>]+)>'
                    city_clear_name = re.sub(pattern, '', elem['caption'])
                    cities.append({'city_name': city_clear_name,
                                   'destination_id': elem['destinationId']
                                   }
                                  )
        except Exception:
            cities = None
        return cities
    return None


def print_cities(cities):
    """
    Клавиатура с кнопками - выбор подходящего по названию города, из которых пользователь выбирает нужный ему.
    :param cities_dict: словарь с названиями городов и их id.
    :return: клавиатура InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    for city in cities:
        keyboard.add(InlineKeyboardButton(text=city['city_name'], callback_data=f'city_id:{city["destination_id"]}'))

    keyboard.add(InlineKeyboardButton(text="Выйти в меню", callback_data='exit'))
    return keyboard


def print_cities_bestdeal(cities):
    """
    Клавиатура с кнопками - выбор подходящего по названию города, из которых пользователь выбирает нужный ему.
    :param cities_dict: словарь с названиями городов и их id.
    :return: клавиатура InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    for city in cities:
        keyboard.add(InlineKeyboardButton(text=city['city_name'],
                                            callback_data=f'bestdeal_id:{city["destination_id"]}'))

    keyboard.add(InlineKeyboardButton(text="Выйти в меню", callback_data='exit'))
    return keyboard


if __name__ == '__main__':
    pass