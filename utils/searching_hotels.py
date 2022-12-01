import re
import requests
from datetime import date
from typing import Union, Dict, List
from telebot.types import InputMediaPhoto
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from loader import api_headers


@logger.catch()
def get_result_with_photos(hotel_id_value: int, hotels_photo_count: int, text: str):
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
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

    querystring = {"id": str(hotel_id_value)}

    response = requests.get(url, headers=api_headers, params=querystring)

    if response and response.text != '':
        result = list()
        photo_hotel_get = response.json()['hotelImages']
        for photo in photo_hotel_get:
            try:
                photo_url = photo['baseUrl']
                photo_size = [size['suffix'] for size in photo['sizes'] if size['suffix'] in ["z", "y"]][0]
                result.append(photo_url.format(size=photo_size))
            except Exception:
                result = None
        if len(result) >= hotels_photo_count:
            photos_urls = result[:hotels_photo_count]
            photo_mosaic = [InputMediaPhoto(media=url, caption=text) if index == 0
                            else InputMediaPhoto(media=url) for index, url in enumerate(photos_urls)]
            return photo_mosaic, photos_urls
    else:
        return None


@logger.catch()
def get_hotels_info(command: str, city_id: str, hotels_count: str, date_in: date, date_out: date, photo_count: int = 0):
    """
    Функция отправляет запрос на заданный url с заданными параметрами, десериализует, обрабатывает результат
    и получает информацию об отелях в городе, найденном по его id в разделе "lowprice" and "highprice".
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
    url = "https://hotels4.p.rapidapi.com/properties/list"
    if command == "lowprice":
        querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": str(hotels_count),
                       "checkIn": str(date_in), "checkOut": str(date_out), "adults1": "1",
                       "sortOrder": "PRICE", "locale": "ru_RU", "currency": "RUB"}
    elif command == "highprice":
        querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": str(hotels_count),
                       "checkIn": str(date_in), "checkOut": str(date_out), "adults1": "1",
                       "sortOrder": "PRICE_HIGHEST_FIRST", "locale": "ru_RU", "currency": "RUB"}
    response = requests.get(url, headers=api_headers, params=querystring)
    try:
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
                hotel_url = 'https://www.hotels.com/h' + str(hotel_id) + '.Hotel-Information/'
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
    except Exception as exp:
        print('Не удалось подключиться к серверу.', exp)
        return None


@logger.catch()
def get_hotels_info_bestdeal(city_id: str, hotels_count: str, date_in: date,
                             date_out: date, distance: float, price: str,
                             photo_count: int = 0, command: str = "bestdeal"):
    """
    Функция отправляет запрос на заданный url с заданными параметрами, десериализует, обрабатывает результат
    и получает информацию об отелях в городе, найденном по его id в разделе "bestdeal".
    Если пользователь ввел запрос с нахождением фотографий, то редактирует текст, согласно найденной информации об отеле
    и вызывает функцию, которая ищет фотографии отеля и возвращает их в готовом для вывода виде. И считает количество найденных отелей.
    Если пользователь ищет без фотографий, то возвращает текст поиска в виде списка, чтобы корректно его обработать в БД.
    Если количество фотографий и количество найденных отелей равно 0: возвращает None.
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
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": str(city_id), "pageNumber": "1", "pageSize": "25", "checkIn": str(date_in),
                   "checkOut": str(date_out), "adults1": "1", "sortOrder": "PRICE", "locale": "ru_RU",
                   "currency": "RUB"}

    response = requests.get(url, headers=api_headers, params=querystring)

    hotels_counter = 0  # счётчик количества найденных отелей.

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
            if not int(num[0] + num[1]) >= int(price) and not float(
                    distance_from_center[:-3].replace(',', '.')) >= float(distance):

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
        except Exception:
            pass
    if photo_count == 0 and hotels_counter == 0:
        return None


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
