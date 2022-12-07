# -*- coding: utf-8 -*-
from telebot import types, custom_filters
from telebot.types import Message, CallbackQuery

from loader import bot
from utils.searching_hotels import *
from utils import calendar
from handlers import start
from database import history
from states.new_states import LowHighStates


@logger.catch()
def command_get(message: Message, command: str) -> None:
	"""
	Функция, реагирующая на выбор пользователем действия поиска и предлагающая ввести название города.

	:param message: сообщение Telegram
	"""
	bot.set_state(message.from_user.id, LowHighStates.city, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['command'] = command


def menu(message):
	"""
	Функция, возвращающая в главное меню и обнуляющая состояния

	:param message: сообщение Telegram
	"""
	start.bot_start(message)
	bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=LowHighStates.city, is_digit=False)
@logger.catch()
def city_get(message: Message) -> None:
	"""
	Функция, ожидающая корректный ввод города, без цифр. Состояние пользователя - 'city_lowprice'.
	Временно записывает данные о городах и об id пользователя для дальнейшей обработки.
	Показывает клавиатуру с выбором конкретного города для уточнения.

	:param message: сообщение Telegram
	"""
	cities = get_city_name_and_id(message.text)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['cities'] = cities
		data['user_id'] = message.from_user.id
		if cities:
			bot.send_message(message.from_user.id, 'Пожалуйста, уточните:', reply_markup=print_cities(cities))
			if data['command'] == "bestdeal":
				bot.set_state(message.from_user.id, LowHighStates.price_to, message.chat.id)
			else:
				bot.set_state(message.from_user.id, LowHighStates.hotels_count, message.chat.id)
		else:
			bot.send_message(message.from_user.id, 'Не нахожу такой город. Введите ещё раз.')


@bot.callback_query_handler(lambda call: call.data.startswith('city_id:'))
@logger.catch()
def choose_city(call: CallbackQuery) -> None:
	"""
	Функция, реагирующая на нажатие кнопки с выбором конкретного города.
	Временно записывает данные об id и названии выбранного города для дальнейшей обработки.
	Предлагает выбрать определенное количество отелей для поиска, либо вернуться в меню.

	:param call: отклик клавиатуры.
	"""
	bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
	bot.delete_message(call.message.chat.id, call.message.message_id)

	with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
		data['city_id'] = re.search(r'\d+', call.data).group()
		data['city'] = [city['city_name'] for city in data['cities'] if city["destination_id"] == data['city_id']][0]
		if data['command'] == "bestdeal":
			bot.send_message(call.message.chat.id, 'Введите желаемую максимальную стоимость комнаты за сутки в $:')
		else:
			markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
			item1, item2, item3 = types.KeyboardButton("3"), types.KeyboardButton("6"), types.KeyboardButton("9")
			item4 = types.KeyboardButton("Вернуться в меню")
			markup.add(item1, item2, item3)
			markup.add(item4)
			bot.send_message(call.message.chat.id, "Какое количество отелей будем искать?", reply_markup=markup)


@bot.callback_query_handler(lambda call: call.data == 'exit')
@logger.catch()
def back_to_menu(call: CallbackQuery) -> None:
	"""
	Функция, реагирующая на нажатие кнопки "Выйти в меню" при выборе варианта с городами.
	Удаляет состояние и вызывает главное меню.

	:param call: отклик клавиатуры.
	"""
	bot.delete_state(call.message.chat.id, call.message.chat.id)
	start.bot_start(call.message)


@bot.message_handler(state=LowHighStates.price_to, is_digit=True)
@logger.catch()
def price_to_get(message: Message) -> None:
	"""
	Функция, ожидающая корректный ввод количества рублей в виде числа.
	Предлагает ввести максимальное расстояние удаления отеля от центра города.
	Если цена меньше нуля, то приравнивает к нулю и временно записывает данные
	о максимальной цене за ночь в отеле	для дальнейшей обработки.

	:param message: сообщение Telegram
	"""
	bot.send_message(message.chat.id,
					 f"Введите расстояние в метрах, на котором может находиться отель от центра.")
	bot.set_state(message.from_user.id, LowHighStates.dist_from_center, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['price_to'] = int(message.text)
		if data['price_to'] < 0:
			data['price_to'] = 0


@bot.message_handler(state=LowHighStates.price_to, is_digit=False)
@logger.catch()
def price_to_incorrect(message: Message) -> None:
	"""
	Функция, воспроизводящаяся при вводе максимальной цены не цифрами.
	Если максимальная цена не число - просит ввести еще раз.

	:param message: сообщение Telegram
	"""
	bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.message_handler(state=LowHighStates.dist_from_center, is_digit=True)
@logger.catch()
def dist_from_center(message: Message) -> None:
	"""
	Функция, ожидающая ввод максимального расстояния нахождения отеля от центра в виде числа.
	Если расстояние меньше 0, то просит ввести еще раз.
	В ином случае: предлагает выбрать определенное количество отелей для поиска, либо вернуться в меню.
	Временно записывает данные о желаемом расстоянии отеля от центра для дальнейшей обработки.

	:param message: сообщение Telegram
	"""
	dist_from_center_to = message.text
	if int(dist_from_center_to) < 0:
		bot.reply_to(message,
					 """Расстояние не может быть меньше 0.\nПопробуйте еще раз""")
		bot.set_state(message.from_user.id, LowHighStates.dist_from_center, message.chat.id)
	else:
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		item1, item2, item3 = types.KeyboardButton("3"), types.KeyboardButton("6"), types.KeyboardButton("9")
		item4 = types.KeyboardButton("Вернуться в меню")
		markup.add(item1, item2, item3)
		markup.add(item4)
		bot.send_message(message.chat.id, "Какое количество отелей будем искать?", reply_markup=markup)
		bot.set_state(message.from_user.id, LowHighStates.hotels_count, message.chat.id)
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['dist_from_center_to'] = dist_from_center_to


@bot.message_handler(state=LowHighStates.hotels_count, is_digit=False)
@logger.catch()
def hotels_count_incorrect(message: Message) -> None:
	"""
	Функция, воспроизводящаяся при вводе количества отелей не цифрами.
	Если сообщение имеет значение "Вернуться в меню", то удаляет состояние и вызывает главное меню.
	Иначе - просит ввести еще раз.

	:param message: сообщение Telegram
	"""
	if message.text == "Вернуться в меню":
		menu(message)
	else:
		bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.message_handler(state=LowHighStates.hotels_count, is_digit=True)
@logger.catch()
def hotels_count_step(message: Message) -> None:
	"""
	Функция, ожидающая корректный ввод количества отелей в виде цифр и округляющая результат до определенного параметра.
	Показывает клавиатуру с вопросом о необходимости загрузить фото отелей. Варианты ответа: 'Да' и 'Нет'.
	Временно записывает данные о количестве отелей для дальнейшей обработки.

	:param message: сообщение Telegram
	"""
	hotels_count = message.text
	if 3 > int(hotels_count):
		hotels_count = 3
	elif 3 < int(hotels_count) <= 6:
		hotels_count = 6
	elif 9 < int(hotels_count) or (6 < int(hotels_count) <= 9):
		hotels_count = 9
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	item1, item2 = types.KeyboardButton("Да"), types.KeyboardButton("Нет")
	item3 = types.KeyboardButton("Вернуться в меню")
	markup.add(item1, item2)
	markup.add(item3)
	bot.send_message(message.chat.id, 'Показывать фотографии отеля?', reply_markup=markup)
	bot.set_state(message.from_user.id, LowHighStates.load_photo, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['hotels_count'] = hotels_count


@bot.message_handler(state=LowHighStates.load_photo)
@logger.catch()
def load_photo_step(message: Message) -> None:
	"""
	Функция, реагирующая на нажатие кнопки 'Да' и 'Нет'(либо другой вариант) о необходимости загрузить фото отелей.
	Если ответ 'да': предлагает выбрать количество фото на клавиатуре.
	Если ответ 'нет': показывает клавиатуру-календарь с выбором даты заезда.
	Если ответ 'Вернуться в меню': удаляет состояния и выводит главное меню.

	:param message: сообщение Telegram
	"""
	load_photo = message.text
	if load_photo == u'Да':
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		item1, item2, item3 = types.KeyboardButton("1"), types.KeyboardButton("3"), types.KeyboardButton("5")
		item4 = types.KeyboardButton("Вернуться в меню")
		markup.add(item1, item2, item3)
		markup.add(item4)
		bot.reply_to(message, "Количество фотографий:", reply_markup=markup)
		bot.set_state(message.from_user.id, LowHighStates.photo_count, message.chat.id)
	elif load_photo == "Вернуться в меню":
		menu(message)
	else:
		calendar.calendar_in(message)


@bot.message_handler(state=LowHighStates.photo_count, is_digit=True)
@logger.catch()
def photo_count_step(message: Message) -> None:
	"""
	Функция, ожидающая корректный ввод количества фото в виде цифр и округляющая результат до определенного параметра..
	Показывает клавиатуру-календарь с выбором даты заезда.
	Временно записывает данные о количестве разыскиваемых отелей для дальнейшей обработки.

	:param message: сообщение Telegram
	"""
	photo_count = message.text
	if int(photo_count) <= 1:
		message.text = 1
	elif 1 < int(photo_count) <= 3:
		message.text = 3
	elif 5 < int(photo_count) or (3 < int(photo_count) <= 5):
		message.text = 5
	calendar.calendar_in(message)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['photo_count'] = message.text


@bot.message_handler(state=LowHighStates.photo_count, is_digit=False)
@logger.catch()
def photo_count_incorrect(message: Message) -> None:
	"""
	Функция, ожидающая некорректный ввод воспроизводящаяся при вводе количества фото не цифрами.
	Если сообщение имеет значение "Вернуться в меню", то удаляет состояние и вызывает главное меню.
	Иначе - просит ввести еще раз.

	:param message: сообщение Telegram
	"""
	if message.text == "Вернуться в меню":
		menu(message)
	else:
		bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@logger.catch()
def ready_for_answer(message: Message) -> None:
	"""
	Функция обрабатывает полученные данные, делает запрос на парсинг отелей, выводит полученный результат
	в зависимости от того, желал ли пользователь видеть фотографии или нет, и добавляет результат в БД.
	Если в результате получает ошибку - возвращает в главное меню и просит пользователя ввести данные дальнейшую команду.

	:param message: сообщение Telegram
	"""
	info_for_history = list()
	with bot.retrieve_data(message.chat.id, message.chat.id) as data:
		user_id: int = data['user_id']
		hotels_count: str = data['hotels_count']
		date_in: date = data['dateIn']
		date_out: date = data['dateOut']
		city_name: str = data['city']
		city_id: str = data['city_id']
		command: str = data['command']
		if command != "bestdeal":
			msg = (f"<b>🏨Город: {city_name}\n"
				   f"📆Длительность поездки: с {date_in} по {date_out}\n"
				   f"🔢Количество отелей: {hotels_count}\n</b>")
		else:
			max_price: int = data['price_to']
			max_distance: float = int(data['dist_from_center_to']) / 1000
			msg = (f"<b>🏨Город: {city_name}\n"
				   f"📆Длительность поездки: с {date_in} по {date_out}\n"
				   f"💰Ценовой диапазон: 0 - {max_price}\n"
				   f"🗺Расстояние от центра: 0 - {max_distance}\n"
				   f"🔢Количество отелей: {hotels_count}\n</b>")
		try:
			photo_count: int = data['photo_count']
			photo_count_exist = f"📷Фотографии: {photo_count} шт.\n</b>"
			msg = msg[:-4] + photo_count_exist
		except:
			pass

		bot.send_message(message.chat.id, msg, parse_mode="html", )
		bot.send_message(message.chat.id, "Ищем по запросу...")

		if 'photo_count' not in locals():
			if command != "bestdeal":
				for hotel_info in get_hotels_info(command, city_id, hotels_count, date_in, date_out):
					bot.send_message(message.chat.id, hotel_info, parse_mode="html")
					info_for_history.append(hotel_info)
			else:
				for hotel_info in get_hotels_info(command, city_id, hotels_count, date_in,
												  date_out, max_distance, max_price):
					if hotel_info == str:
						bot.send_message(message.chat.id, hotel_info, parse_mode="html")
					else:
						bot.send_message(message.chat.id, hotel_info, parse_mode="html")
						info_for_history.append(hotel_info)
			history.history_add(user_id, command, str(info_for_history))
		else:
			photo_info_history = list()
			if command != "bestdeal":
				for result, photos_url, text in get_hotels_info(command, city_id, hotels_count,
																date_in, date_out, photo_count=photo_count):
					bot.send_media_group(message.chat.id, media=result)
					info_for_history.append(text)
					photo_info_history.append(photos_url)
			else:
				for hotel_info, photos_url, text in get_hotels_info(command, city_id, hotels_count, date_in, date_out,
																			 max_distance, max_price, photo_count):
					bot.send_media_group(message.chat.id, media=hotel_info)
					info_for_history.append(text)
					photo_info_history.append(photos_url)
				if len(photo_info_history) < int(hotels_count):
					bot.send_message(message.chat.id, "Это всё, что удалось найти🤷‍♂")
			history.history_add(user_id, command, str(info_for_history), str(photo_info_history))
	start.bot_start(message)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
