from utils import coordinates_calc
import re

from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup

from loader import bot
from handlers import start
from database import history


class MyStates(StatesGroup):
	city_bestdeal = State()
	price_from_bestdeal = State()
	price_to_bestdeal = State()
	dist_from_center_from_bestdeal = State()
	dist_from_center_to_bestdeal = State()
	hotels_count_bestdeal = State()
	load_photo_bestdeal = State()
	photo_count_bestdeal = State()


@bot.message_handler(commands=['bestdeal'])
def bestdeal_menu(message):
	bot.send_message(message.chat.id, 'Давай подберем подходящий отель!\nКакой город?')
	bot.set_state(message.from_user.id, MyStates.city_bestdeal, message.chat.id)


# @bot.message_handler(state="*", commands=['cancel'])
# def any_state(message):
# 	"""
# 	Cancel state
# 	"""
# 	bot.send_message(message.chat.id, "Your state was cancelled.")
# 	bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.city_bestdeal)
def city_get(message):
	bot.send_message(message.chat.id, 'Введите желаемую минимальную стоимость комнаты за ночь в долларах:')
	bot.set_state(message.from_user.id, MyStates.price_from_bestdeal, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['city'] = message.text


@bot.message_handler(state=MyStates.price_from_bestdeal, is_digit=True)
def price_from_get(message):
	bot.send_message(message.chat.id, 'Введите максимальную сумму, которую готовы потратить за комнату:')
	bot.set_state(message.from_user.id, MyStates.price_to_bestdeal, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['price_from'] = message.text


@bot.message_handler(state=MyStates.price_to_bestdeal, is_digit=True)
def price_to_get(message):
	format_example = 'Формат: <Min расстояние>  <Max расстояние>'
	bot.send_message(message.chat.id,
					 f"Введите диапазон расстояния в метрах, на котором будет находиться отель от центра.\n{format_example}")
	bot.set_state(message.from_user.id, MyStates.dist_from_center_to_bestdeal, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['price_to'] = message.text
		if data['price_to'] < data['price_from']:
			data['price_to'] = data['price_from']


@bot.message_handler(state=MyStates.price_from_bestdeal, is_digit=False)
def price_from_incorrect(message):
	bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.message_handler(state=MyStates.price_to_bestdeal, is_digit=False)
def price_to_incorrect(message):
	bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.message_handler(state=MyStates.dist_from_center_to_bestdeal)
def dist_from_center(message):
	if re.fullmatch(r'\d+\s+\d+', str(message.text)) is None:
		bot.reply_to(message, "Неверный формат. Проверьте правильность и попробуйте еще раз")
		bot.set_state(message.from_user.id, MyStates.dist_from_center_to_bestdeal, message.chat.id)
		return
	else:
		dist_from_center_from, dist_from_center_to = message.text.split()
		if dist_from_center_to < dist_from_center_from:
			bot.reply_to(message,
						 """Минимальное расстояние не может быть больше максимального.\nПопробуйте еще раз""")
			bot.set_state(message.from_user.id, MyStates.dist_from_center_to_bestdeal, message.chat.id)
			return
		else:
			markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
			item1, item2, item3 = types.KeyboardButton("3"), types.KeyboardButton("6"), types.KeyboardButton("9")
			markup.add(item1, item2, item3)
			bot.send_message(message.chat.id, "Какое количество отелей будем искать?", reply_markup=markup)
			bot.set_state(message.from_user.id, MyStates.hotels_count_bestdeal, message.chat.id)
			with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
				data['dist_from_center_from'] = dist_from_center_from
				data['dist_from_center_to'] = dist_from_center_to


@bot.message_handler(state=MyStates.dist_from_center_to_bestdeal, is_digit=False)
def price_to_incorrect(message):
	bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


@bot.message_handler(state=MyStates.hotels_count_bestdeal, is_digit=True)
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
	markup.add(item1, item2)
	bot.send_message(message.chat.id, 'Показывать фотографии отеля?', reply_markup=markup)
	bot.set_state(message.from_user.id, MyStates.load_photo_bestdeal, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['hotels_count'] = hotels_count


@bot.message_handler(state=MyStates.load_photo_bestdeal)
def load_photo_step(message):
	load_photo = message.text
	if load_photo == u'Да':
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		item1, item2, item3 = types.KeyboardButton("1"), types.KeyboardButton("3"), types.KeyboardButton("5")
		markup.add(item1, item2, item3)
		bot.reply_to(message, "Количество фотографий:", reply_markup=markup)
		bot.set_state(message.from_user.id, MyStates.photo_count_bestdeal, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'Тогда вот что мы нашли!')
		ready_for_answer(message)


@bot.message_handler(state=MyStates.photo_count_bestdeal, is_digit=True)
def photo_count_step(message):
	photo_count = message.text
	if int(photo_count) <= 1:
		message.text = 1
	elif 1 < int(photo_count) <= 3:
		message.text = 3
	elif 5 < int(photo_count) or (3 < int(photo_count) <= 5):
		message.text = 5
	bot.send_message(message.chat.id, 'Тогда вот что мы нашли!')
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['photo_count'] = message.text
	ready_for_answer(message)


@bot.message_handler(state=MyStates.photo_count_bestdeal, is_digit=False)
def photo_count_incorrect(message):
	bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


def ready_for_answer(message):
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		msg = ("Ready, take a look:\n<b>"
			   f"City: {data['city']}\n"
			   f"Price range: {data['price_from']} - {data['price_to']}\n"
			   f"Distance range: {data['dist_from_center_from']} - {data['dist_from_center_to']}\n"			   
			   f"Hotels count: {data['hotels_count']}\n</b>")
		try:
			photo_count_exist = f"Photo count: {data['photo_count']}\n</b>"
			msg = msg[:-4] + photo_count_exist
			photo_count = data['photo_count']
		except:
			pass

		user_id = message.from_user.id
		hotel_info = data['hotels_count']
		city_name = data['city']
		min_price, max_price = data['price_from'], data['price_to']
		min_distance, max_distance = data['dist_from_center_from'], data['dist_from_center_to']
		bot.send_message(message.chat.id, msg, parse_mode="html")

	if 'photo_count' not in locals():
		history.best_history_add(user_id, "bestdeal", city_name, min_price, max_price, min_distance, max_distance, hotel_info)
	else:
		history.best_history_add(user_id, "bestdeal", city_name, min_price, max_price,
								 min_distance, max_distance, hotel_info, photo_count)
	bot.delete_state(message.from_user.id, message.chat.id)
	start.bot_start(message)



bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
