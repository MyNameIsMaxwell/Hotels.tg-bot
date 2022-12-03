import re
import requests
from datetime import date
from typing import Union, Dict, List
from telebot.types import InputMediaPhoto
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from loader import api_headers
from config_data import config
from . import payloads


@logger.catch()
def get_result_with_photos(hotel_id_value: str, hotels_photo_count: int, text: str):
    """
    Функция отправляет запрос на заданный url с параметром id отеля, десериализует, обрабатывает результат
    и получает список фотографий отеля, который преобразует в удобную для вывода в чат форму.
    :param hotel_id_value: (int) id отеля, по которому проводится поиск.
    :param hotels_photo_count: (int) желаемое количество фотографий отеля.
    :param text: (str) текстовая информация об отеле для того, чтобы подписать первую фотографию для корректного вывода в чате.
    :return: photo_mosaic, photos_urls: List[InputMediaPhoto], List[str] фотографии в виде, подходящим для вывода и
    список со ссылками на фотографии отеля.
    :return: None, если не удалось подключиться.
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {"propertyId": hotel_id_value}

    response = requests.request("POST", url, json=payload, headers=api_headers)
    try:
        photos_urls = list()
        for hotel_photo_value in response.json()["data"]["propertyInfo"]["propertyGallery"]["images"]:
            photos_urls.append(hotel_photo_value["image"]["url"])
            if len(photos_urls) >= hotels_photo_count:
                photos_urls = photos_urls[:hotels_photo_count]
                photo_mosaic = [InputMediaPhoto(media=url, caption=text) if index == 0
                                else InputMediaPhoto(media=url) for index, url in enumerate(photos_urls)]
                return photo_mosaic, photos_urls
        else:
            return None
    except Exception:
        print("Невозможно загрузить фото")


@logger.catch()
def get_address_info(hotel_id: str):
    """
    Функция отправляет запрос на заданный url с параметром id отеля, десериализует, обрабатывает результат
    и получает адрес отеля.
    :param hotel_id: (int) id отеля, по которому проводится поиск.
    :return: hotel_address: (str) адрес отеля.
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {
        "currency": "USD",
        "locale": "ru_RU",
        "propertyId": hotel_id
    }

    response = requests.request("POST", url, json=payload, headers=api_headers)
    hotel_address = response.json()["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
    return hotel_address


@logger.catch()
def get_hotels_info(command: str, city_id: str, hotels_count: str, date_in: date, date_out: date, photo_count: int = 0):
    """
    Функция отправляет запрос на заданный url с заданными параметрами, полученными из payload, десериализует, обрабатывает
    результат и получает информацию об отелях в городе.
    Если пользователь ввел запрос с нахождением фотографий, то редактирует текст, согласно найденной информации об отеле
    и вызывает функцию, которая ищет фотографии отеля и возвращает их в готовом для вывода виде. И считает количество найденных отелей.
    Если пользователь ищет без фотографий, то возвращает текст поиска в виде списка, чтобы корректно его обработать в БД.
    Если ошибка при поиске информации об отеле: возвращает None.
    :param command: (str) название выбранной операции поиска.
    :param city_id: (str) id города, в котором пользователь ищет отели.
    :param hotels_count: (str) разыскиваемое количество отелей в городе.
    :param date_in: (date) дата въезда в отель.
    :param date_out: (date) дата выезда из отеля.
    :param photo_count: (int) количество фотографий отеля.

    :return: result, photos, text: Union[List[InputMediaPhoto], List[str], List[str]] фотографии для отправки, список с
    url фотографий, текст сообщения, если запрос с фотографиями.
    :return: text: List[str]] текст сообщения, если запрос без фотографий.
    :return: None
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = payloads.low_high_price_payload(command, city_id, hotels_count, str(date_in), str(date_out))

    response = requests.request("POST", url, json=payload, headers=api_headers)
    try:
        for hotel_id_value in response.json()["data"]["propertySearch"]["properties"]:
            try:
                hotel_id = hotel_id_value["id"]
                hotel_name = hotel_id_value["name"]
                hotel_address = get_address_info(hotel_id)
                distance_from_center = hotel_id_value["destinationInfo"]["distanceFromDestination"]["value"]
                days = date_out - date_in
                price_one_day = hotel_id_value["price"]["options"][0]["formattedDisplayPrice"]
                num = re.findall(r'\d+', price_one_day)
                sum_price = days.days * int(num[0])
                all_days_price = str(sum_price) + "$"
                hotel_url = 'https://www.hotels.com/h' + str(hotel_id) + '.Hotel-Information/'
                msg = (f"<b>Отель: {hotel_name}\n"
                       f"Адрес: {hotel_address}\n"
                       f"Расстояние до центра: {distance_from_center} км\n"
                       f"Цена за 1 сутки: {price_one_day}\n"
                       f"Стоимость за {days.days} суток: {all_days_price}\n"
                       f"Подробнее об отеле: {hotel_url}\n</b>")
                if int(photo_count) > 0:
                    text = msg.replace("<b>", '').replace("</b>", '')
                    result, photos = get_result_with_photos(hotel_id, photo_count, text)
                    yield result, photos, [text]
                else:
                    yield [msg]
            except Exception as exp:
                print(exp)
    except Exception as exp:
        print('Не удалось подключиться к серверу.', exp)
        yield None


@logger.catch()
def get_hotels_info_bestdeal(city_id: str, hotels_count: str, date_in: date,
                             date_out: date, distance: float, price: str,
                             photo_count: int = 0, command: str = "bestdeal"):
    """
    Функция отправляет запрос на заданный url с заданными параметрами, полученными из payload, десериализует, обрабатывает
    результат и получает информацию об отелях в городе.
    Если пользователь ввел запрос с нахождением фотографий, то редактирует текст, согласно найденной информации об отеле
    и вызывает функцию, которая ищет фотографии отеля и возвращает их в готовом для вывода виде. И считает количество найденных отелей.
    Если пользователь ищет без фотографий, то возвращает текст поиска в виде списка, чтобы корректно его обработать в БД.
    Если количество фотографий равно нулю и количество найденных отелей меньше разыскиваемых: возвращает сообщение об этом.
    :param city_id: (str) id города, в котором пользователь ищет отели.
    :param hotels_count: (str) разыскиваемое количество отелей в городе.
    :param date_in: (date) дата въезда в отель.
    :param date_out: (date) дата выезда из отеля.
    :param distance: (float) желаемое расстояние отеля от центра города.
    :param price: (str) желаемая стоимость ночи в отеле.
    :param photo_count: (int) количество фотографий отеля.
    :param command: (str) название выбранной операции поиска.

    :return: result, photos, text: Union[List[InputMediaPhoto], List[str], List[str]] фотографии для отправки, список с
    url фотографий, текст сообщения, если запрос с фотографиями.
    :return: text: List[str]] текст сообщения, если запрос без фотографий.
    :return: None
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    payload = payloads.bestdeal_payload(city_id, int(hotels_count), int(price), str(date_in), str(date_out))

    response = requests.request("POST", url, json=payload, headers=api_headers)

    hotels_counter = 0  # счётчик количества найденных отелей.

    for hotel_id_value in response.json()["data"]["propertySearch"]["properties"]:
        try:
            if hotels_counter == int(hotels_count):
                break
            hotel_id = hotel_id_value["id"]
            hotel_name = hotel_id_value["name"]
            hotel_address = get_address_info(hotel_id)
            distance_from_center = hotel_id_value["destinationInfo"]["distanceFromDestination"]["value"]
            days = date_out - date_in
            price_one_day = hotel_id_value["price"]["options"][0]["formattedDisplayPrice"]
            num = re.findall(r'\d+', price_one_day)
            sum_price = days.days * int(num[0])
            all_days_price = str(sum_price) + "$"
            hotel_url = 'https://www.hotels.com/h' + str(hotel_id) + '.Hotel-Information/'
            if not float(distance_from_center) >= float(distance):
                msg = (f"<b>Отель: {hotel_name}\n"
                       f"Адрес: {hotel_address}\n"
                       f"Расстояние до центра: {distance_from_center} км\n"
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
        except Exception:
            pass
    if photo_count == 0 and hotels_counter < int(hotels_count):
        yield "Это всё, что удалось найти🤷‍♂"


@logger.catch()
def get_city_name_and_id(city: str) -> Union[List[Dict[str, str]], None]:
    """
    Функция отправляет запрос на заданный url с заданными параметрами, десериализует, обрабатывает результат
    и получает список городов по запросу.
    Если соединение прошло успешно: преобразуем в json и получаем информацию о городе(-ах) в виде словаря. Выбираем из
    него информацию об destinationId и имени города(-ов), и добавляем в виде словаря в список. Если выдается ошибка, то
    список равен None. Возвращаем этот словарь.
    Если соединение не установлено: возвращает None.
    :param city: (str) название города введенное с клавиатуры пользователем.
    :return: cities or None: Union[List[str, str], None] список с названиями городов и их id или None.
    """
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city, "locale": "ru_RU"}
    headers = {"X-RapidAPI-Key": config.RAPID_API_KEY, "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    hotels_api = requests.get(url, headers=headers, params=querystring)
    if hotels_api.status_code == 200:
        cities = list()
        try:
            for elem in hotels_api.json()["sr"]:
                if elem["type"] == "CITY":
                    city_clear_name = elem['regionNames']['fullName']
                    cities.append({'city_name': city_clear_name,
                                   'destination_id': elem['gaiaId']
                                   }
                                  )
        except Exception:
            cities = None
        return cities
    return None


@logger.catch()
def print_cities(cities: Union[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками - выбор подходящего по названию города, из которых пользователь выбирает нужный ему.
    :param cities: Union[List[Dict[str, str]]] словарь с названиями городов и их id.
    :return: клавиатура InlineKeyboardMarkup.
    """
    keyboard = InlineKeyboardMarkup(row_width=1)
    for city in cities:
        keyboard.add(InlineKeyboardButton(text=city['city_name'], callback_data=f'city_id:{city["destination_id"]}'))

    keyboard.add(InlineKeyboardButton(text="Выйти в меню", callback_data='exit'))
    return keyboard


@logger.catch()
def print_cities_bestdeal(cities: Union[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
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
