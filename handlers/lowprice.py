from telebot import types, custom_filters
from telebot.types import Message, CallbackQuery
from datetime import timedelta
from telegram_bot_calendar import DetailedTelegramCalendar

from loader import bot
from handlers import start
from database import history
from utils.searching_hotels import *
from states.states import MyStatesLowprice


@bot.message_handler(commands=['lowprice'])
@logger.catch()
def lowprice_menu(message: Message) -> None:
	"""
	Функция, реагирующая на команду 'lowprice' и предлагающая ввести название города.

	:param message: сообщение Telegram
	"""
	bot.send_message(message.chat.id, 'Давай узнаем топ самых дешёвых отелей в городе!\nКакой город?')
	bot.set_state(message.from_user.id, MyStatesLowprice.city_lowprice, message.chat.id)


@bot.message_handler(state=MyStatesLowprice.city_lowprice, is_digit=False)
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
		bot.set_state(message.from_user.id, MyStatesLowprice.hotels_count_lowprice, message.chat.id)
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


@bot.message_handler(state=MyStatesLowprice.hotels_count_lowprice, is_digit=False)
@logger.catch()
def hotels_count_incorrect(message: Message) -> None:
	"""
	Функция, воспроизводящаяся при вводе количества отелей не цифрами.
	Если сообщение имеет значение "Вернуться в меню", то удаляет состояние и вызывает главное меню.
	Иначе - просит ввести еще раз.

	:param message: сообщение Telegram
	"""
	if message.text == "Вернуться в меню":
		start.bot_start(message)
		bot.delete_state(message.from_user.id, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.message_handler(state=MyStatesLowprice.hotels_count_lowprice, is_digit=True)
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
	bot.set_state(message.from_user.id, MyStatesLowprice.load_photo_lowprice, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['hotels_count'] = hotels_count


@bot.message_handler(state=MyStatesLowprice.load_photo_lowprice)
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
		bot.set_state(message.from_user.id, MyStatesLowprice.photo_count_lowprice, message.chat.id)
	elif load_photo == "Вернуться в меню":
		start.bot_start(message)
		bot.delete_state(message.from_user.id, message.chat.id)
	else:
		calendar, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
												  max_date=date.today() + timedelta(days=730), locale='ru',
												  calendar_id="lowprice1").build()
		bot.send_message(message.chat.id,
						 f"Введите дату въезда:",
						 reply_markup=calendar)


@bot.message_handler(state=MyStatesLowprice.photo_count_lowprice, is_digit=True)
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
	calendar, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
											  max_date=date.today() + timedelta(days=730), locale='ru', calendar_id="lowprice1").build()
	bot.send_message(message.chat.id,
					 f"Введите дату въезда:",
					 reply_markup=calendar)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['photo_count'] = message.text


@bot.message_handler(state=MyStatesLowprice.photo_count_lowprice, is_digit=False)
@logger.catch()
def photo_count_incorrect(message: Message) -> None:
	"""
	Функция, ожидающая некорректный ввод воспроизводящаяся при вводе количества фото не цифрами.
	Если сообщение имеет значение "Вернуться в меню", то удаляет состояние и вызывает главное меню.
	Иначе - просит ввести еще раз.

	:param message: сообщение Telegram
	"""
	if message.text == "Вернуться в меню":
		start.bot_start(message)
		bot.delete_state(message.from_user.id, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id="lowprice1"))
@logger.catch()
def calen(call: CallbackQuery) -> None:
	"""
	Функция, реагирующая на нажатие кнопки на клавиатуре-календаре о дате въезда.
	Условия календаря: минимальный вариант выбора даты - завтра, максимальный - два года.
	Временно записывает данные о дате въезда для дальнейшей обработки.

	:param call: отклик клавиатуры.
	"""
	result, key, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
												 max_date=date.today() + timedelta(days=730), locale='ru', calendar_id="lowprice1").process(
		call.data)
	if not result and key:
		bot.edit_message_text(f"Дата въезда:",
							  call.message.chat.id,
							  call.message.message_id,
							  reply_markup=key)
	elif result:
		bot.edit_message_text(f"Дата въезда: {result}",
							  call.message.chat.id,
							  call.message.message_id)

		calendar, step = DetailedTelegramCalendar(min_date=result + timedelta(days=1),
												  max_date=result + timedelta(days=730), locale='ru',
												  calendar_id="lowprice2").build()
		bot.send_message(call.message.chat.id,
						 f"Дата выезда:",
						 reply_markup=calendar)
		if result is not None:
			with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
				data['dateIn'] = result


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id="lowprice2"))
@logger.catch()
def calen(call: CallbackQuery) -> None:
	"""
	Функция, реагирующая на нажатие кнопки на клавиатуре-календаре о дате выезда.
	Условия календаря: минимальный вариант выбора даты - на следующий день после даты въезда,
	максимальный - два года от даты въезда.
	Временно записывает данные о дате выезда для дальнейшей обработки.
	Вызывает функцию, позволяющую получить результат поиска по временным данным, полученных от пользователя.

	:param call: отклик клавиатуры.
	"""
	with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
		date_from = data['dateIn']
		result, key, step = DetailedTelegramCalendar(min_date=date_from + timedelta(days=1),
													 max_date=date_from + timedelta(days=730), locale='ru', calendar_id="lowprice2").process(
			call.data)
	if not result and key:
		bot.edit_message_text(f"Дата выезда:",
							  call.message.chat.id,
							  call.message.message_id,
							  reply_markup=key)
	elif result:
		bot.edit_message_text(f"Дата выезда: {result}",
							  call.message.chat.id,
							  call.message.message_id)

		with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
			data['dateOut'] = result
		ready_for_answer_lowprice(call.message)
		bot.delete_state(call.message.chat.id, call.message.chat.id)


@logger.catch()
def ready_for_answer_lowprice(message: Message) -> None:
	"""
	Функция обрабатывает полученные данные, делает запрос на парсинг отелей, выводит полученный результат
	в зависимости от того, желал ли пользователь видеть фотографии или нет, и добавляет результат в БД.
	Если в результате получает ошибку - возвращает в главное меню и просит пользователя ввести данные дальнейшую команду.

	:param message: сообщение Telegram
	"""
	info_for_history = list()
	with bot.retrieve_data(message.chat.id, message.chat.id) as data:
		msg = (f"<b>🏨Город: {data['city']}\n"
			   f"📆Длительность поездки: с {data['dateIn']} по {data['dateOut']}\n"
			   f"🔢Количество отелей: {data['hotels_count']}\n</b>")
		try:
			photo_count_exist = f"📷Фотографии: {data['photo_count']} шт.\n</b>"
			msg = msg[:-4] + photo_count_exist
			photo_count: int = data['photo_count']
		except:
			pass
		user_id: int = data['user_id']
		hotels_count: str = data['hotels_count']
		date_in: date = data['dateIn']
		date_out: date = data['dateOut']
		city_name: str = data['city']
		city_id: str = data['city_id']
		bot.send_message(message.chat.id, msg, parse_mode="html")
		bot.send_message(message.chat.id, "Ищем по запросу...")
	if 'photo_count' not in locals():
		for hotel_info in get_hotels_info("lowprice", city_id, hotels_count, date_in, date_out):
			bot.send_message(message.chat.id, hotel_info, parse_mode="html")
			info_for_history.append(hotel_info)
		history.history_add(user_id, "lowprice", str(info_for_history))
	else:
		photo_info_history = list()
		for result, photos_url, text in get_hotels_info("lowprice", city_id, hotels_count, date_in, date_out, photo_count):
			bot.send_media_group(message.chat.id, media=result)
			info_for_history.append(text)
			photo_info_history.append(photos_url)
		history.history_add(user_id, "lowprice", str(info_for_history), str(photo_info_history))
	start.bot_start(message)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
