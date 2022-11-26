from telebot import types, custom_filters
from telebot.types import CallbackQuery
from telebot.handler_backends import State, StatesGroup

from datetime import date, timedelta
from telegram_bot_calendar import DetailedTelegramCalendar

from loader import bot
from handlers import start
from database import history
from utils.searching_hotels import *


class MyStates(StatesGroup):
	city_highprice = State()
	hotels_count_highprice = State()
	load_photo_highprice = State()
	photo_count_highprice = State()


@bot.message_handler(commands=['highprice'])
def highprice_menu(message):
	bot.send_message(message.chat.id, "Давай узнаем топ самых дорогих отелей в городе!\nКакой город?")
	bot.set_state(message.from_user.id, MyStates.city_highprice, message.chat.id)


@bot.message_handler(state=MyStates.city_highprice, is_digit=False)
def city_get(message):
	cities = get_city_name_and_id(message.text)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['cities'] = cities
		data['user_id'] = message.from_user.id
	if cities:
		bot.send_message(message.from_user.id, 'Пожалуйста, уточните:', reply_markup=print_cities(cities))
		bot.set_state(message.from_user.id, MyStates.hotels_count_highprice, message.chat.id)
	else:
		bot.send_message(message.from_user.id, 'Не нахожу такой город. Введите ещё раз.')


@bot.callback_query_handler(lambda call: call.data.startswith('city_id:'))
def choose_city(call):
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
def back_to_menu(call):
	bot.delete_state(call.message.chat.id, call.message.chat.id)
	start.bot_start(call.message)


@bot.message_handler(state=MyStates.hotels_count_highprice, is_digit=False)
def hotels_count_incorrect(message):
	if message.text == "Вернуться в меню":
		start.bot_start(message)
		bot.delete_state(message.from_user.id, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.message_handler(state=MyStates.hotels_count_highprice, is_digit=True)
def hotels_count_step(message):
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
	bot.set_state(message.from_user.id, MyStates.load_photo_highprice, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['hotels_count'] = hotels_count


@bot.message_handler(state=MyStates.load_photo_highprice)
def load_photo_step(message):
	load_photo = message.text
	if load_photo == u'Да':
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		item1, item2, item3 = types.KeyboardButton("1"), types.KeyboardButton("3"), types.KeyboardButton("5")
		item4 = types.KeyboardButton("Вернуться в меню")
		markup.add(item1, item2, item3)
		markup.add(item4)
		bot.reply_to(message, "Количество фотографий:", reply_markup=markup)
		bot.set_state(message.from_user.id, MyStates.photo_count_highprice, message.chat.id)
	elif load_photo == "Вернуться в меню":
		start.bot_start(message)
		bot.delete_state(message.from_user.id, message.chat.id)
	else:
		calendar, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
												  max_date=date.today() + timedelta(days=730), locale='ru',
												  calendar_id="highprice1").build()
		bot.send_message(message.chat.id,
						 f"Введите дату въезда:",
						 reply_markup=calendar)


@bot.message_handler(state=MyStates.photo_count_highprice, is_digit=True)
def photo_count_step(message):
	photo_count = message.text
	if int(photo_count) <= 1:
		message.text = 1
	elif 1 < int(photo_count) <= 3:
		message.text = 3
	elif 5 < int(photo_count) or (3 < int(photo_count) <= 5):
		message.text = 5
	calendar, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
											  max_date=date.today() + timedelta(days=730), locale='ru',
											  calendar_id="highprice1").build()
	bot.send_message(message.chat.id,
					 f"Введите дату въезда:",
					 reply_markup=calendar)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['photo_count'] = message.text


@bot.message_handler(state=MyStates.photo_count_highprice, is_digit=False)
def photo_count_incorrect(message):
	if message.text == "Вернуться в меню":
		start.bot_start(message)
		bot.delete_state(message.from_user.id, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id="highprice1"))
def calen(call: CallbackQuery):

	result, key, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
												 max_date=date.today() + timedelta(days=730), locale='ru', calendar_id="highprice1").process(
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
												  calendar_id="highprice2").build()
		bot.send_message(call.message.chat.id,
						 f"Дата выезда:",
						 reply_markup=calendar)
		if result is not None:
			with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
				data['dateIn'] = result


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id="highprice2"))
def calen(call: CallbackQuery):
	with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
		date_from = data['dateIn']
		result, key, step = DetailedTelegramCalendar(min_date=date_from + timedelta(days=1),
													 max_date=date_from + timedelta(days=730), locale='ru', calendar_id="highprice2").process(
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
		bot.send_message(call.message.chat.id, "Ищем по запросу:\n")
		ready_for_answer_highprice(call.message)
		bot.delete_state(call.message.chat.id, call.message.chat.id)


def ready_for_answer_highprice(message):
	info_for_history = list()
	with bot.retrieve_data(message.chat.id, message.chat.id) as data:
		msg = (f"<b>Город: {data['city']}\n"
			   f"Длительность поездки: с {data['dateIn']} по {data['dateOut']}\n"
			   f"Количество отелей: {data['hotels_count']}\n</b>")
		try:
			photo_count_exist = f"Фотографии: {data['photo_count']} шт.\n</b>"
			msg = msg[:-4] + photo_count_exist
			photo_count = data['photo_count']
		except:
			pass
		user_id = data['user_id']
		hotels_count = data['hotels_count']
		date_in = data['dateIn']
		date_out = data['dateOut']
		city_name = data['city']
		city_id = data['city_id']
		bot.send_message(message.chat.id, msg, parse_mode="html")

	if 'photo_count' not in locals():
		for hotel_info in get_hotels_info("highprice", city_id, hotels_count, date_in, date_out):
			bot.send_message(message.chat.id, hotel_info, parse_mode="html")
			info_for_history.append(hotel_info)
		history.history_add(user_id, "highprice", str(info_for_history))
	else:
		for result, photos_url, text in get_hotels_info("highprice", city_id, hotels_count, date_in, date_out, photo_count):
			bot.send_media_group(message.chat.id, media=result)
			info_for_history.append([user_id, text, photos_url])
	start.bot_start(message)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())

