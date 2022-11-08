from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup

from loader import bot
from handlers import start
from database import history


class MyStates(StatesGroup):
	city_highprice = State()
	hotels_count_highprice = State()
	load_photo_highprice = State()
	photo_count_highprice = State()


@bot.message_handler(commands=['highprice'])
def highprice_menu(message):
	bot.send_message(message.chat.id, "Давай узнаем топ самых дорогих отелей в городе!\nКакой город?")
	bot.set_state(message.from_user.id, MyStates.city_highprice, message.chat.id)


# @bot.message_handler(state="*", commands=['cancel'])
# def any_state(message):
# 	"""
# 	Cancel state
# 	"""
# 	bot.send_message(message.chat.id, "Your state was cancelled.")
# 	bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=MyStates.city_highprice)
def city_get(message):
	if any(map(str.isdigit, message.text)) is True:
		bot.reply_to(message, "Название города не может иметь цифр. Попробуйте еще разок")
		bot.set_state(message.from_user.id, MyStates.city_highprice, message.chat.id)
		return
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
	item1, item2, item3 = types.KeyboardButton("3"), types.KeyboardButton("6"), types.KeyboardButton("9")
	markup.add(item1, item2, item3)
	bot.send_message(message.chat.id, "Какое количество отелей будем искать?", reply_markup=markup)
	bot.set_state(message.from_user.id, MyStates.hotels_count_highprice, message.chat.id)
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['city'] = message.text


@bot.message_handler(state=MyStates.hotels_count_highprice, is_digit=False)
def hotels_count_incorrect(message):
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
	markup.add(item1, item2)
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
		markup.add(item1, item2, item3)
		bot.reply_to(message, "Количество фотографий:", reply_markup=markup)
		bot.set_state(message.from_user.id, MyStates.photo_count_highprice, message.chat.id)
	else:
		bot.send_message(message.chat.id, 'Тогда вот что мы нашли!')
		ready_for_answer(message)


@bot.message_handler(state=MyStates.photo_count_highprice, is_digit=True)
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


@bot.message_handler(state=MyStates.photo_count_highprice, is_digit=False)
def photo_count_incorrect(message):
	bot.send_message(message.chat.id, 'Не похоже на число. Введите число, пожалуйста')


def ready_for_answer(message):
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		msg = ("Ready, take a look:\n<b>"
			   f"City: {data['city']}\n"
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
		bot.send_message(message.chat.id, msg, parse_mode="html")

	if 'photo_count' not in locals():
		history.low_high_history_add(user_id, "highprice", city_name, hotel_info)
	else:
		history.low_high_history_add(user_id, "highprice", city_name, hotel_info, photo_count)
	bot.delete_state(message.from_user.id, message.chat.id)
	start.bot_start(message)


bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.add_custom_filter(custom_filters.IsDigitFilter())
