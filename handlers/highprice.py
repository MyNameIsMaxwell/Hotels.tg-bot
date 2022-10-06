from main import bot
from telebot import types
from handlers import start


class HotelSearch:
	def __init__(self):
		self.city: str = ''
		self.hotels_count: int = 0
		self.photo_count: int = 0


user = HotelSearch()


def highprice_menu(message):
	msg = bot.reply_to(message, "Давай узнаем топ самых дорогих отелей в городе!\nКакой город?")
	bot.register_next_step_handler(msg, process_city_step)


def process_city_step(message):
	try:
		city = message.text
		user.city = city
		# передать city в API
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
		item1, item2, item3 = types.KeyboardButton("3"), types.KeyboardButton("6"), types.KeyboardButton("9")
		markup.add(item1, item2, item3)
		msg = bot.reply_to(message, "Какое количество отелей будем искать?", reply_markup=markup)
		bot.register_next_step_handler(msg, hotels_count_step)
	except Exception as exp:
		bot.reply_to(message, 'oooops1')


def hotels_count_step(message):
	try:
		hotels_count = message.text
		if not hotels_count.isdigit():
			msg = bot.reply_to(message, 'Количество отелей должно быть числом')
			bot.register_next_step_handler(msg, hotels_count_step)
			return
		elif 3 > int(hotels_count):
			user.hotels_count = 3
		elif 3 < int(hotels_count) <= 6:
			user.hotels_count = 6
		elif 9 < int(hotels_count) or (6 < int(hotels_count) <= 9):
			user.hotels_count = 9
		markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
		item1, item2 = types.KeyboardButton("Да"), types.KeyboardButton("Нет")
		markup.add(item1, item2)
		msg = bot.reply_to(message, 'Показывать фотографии отеля?', reply_markup=markup)
		bot.register_next_step_handler(msg, load_photo_step)

	except Exception as exp:
		bot.reply_to(message, 'oooops2')


def load_photo_step(message):
	try:
		load_photo = message.text
		if load_photo == u'Да':
			markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
			item1, item2, item3 = types.KeyboardButton("1"), types.KeyboardButton("3"), types.KeyboardButton("5")
			markup.add(item1, item2, item3)
			msg = bot.reply_to(message, "Количество фотографий:", reply_markup=markup)
			bot.register_next_step_handler(msg, load_photo_count_step)
			return
		else:
			bot.reply_to(message, 'Тогда вот что мы нашли!')
			result(message)

	except Exception as exp:
		bot.reply_to(message, 'oooops3')


def load_photo_count_step(message):
	photo_count = message.text
	if not photo_count.isdigit():
		msg = bot.reply_to(message, 'Количество отелей должно быть числом')
		bot.register_next_step_handler(msg, load_photo_count_step)
		return
	elif int(photo_count) <= 1:
		user.photo_count = 1
	elif 1 < int(photo_count) <= 3:
		user.photo_count = 3
	elif 5 < int(photo_count) or (3 < int(photo_count) <= 5):
		user.photo_count = 5
	bot.reply_to(message, 'Вот что мы нашли!')
	result(message)


def result(message):
	if user.hotels_count == 3:
		bot.send_message(message.chat.id, '3 лучших отеля:')
	elif user.hotels_count == 6:
		bot.send_message(message.chat.id, '6 лучших отелей:')
	elif user.hotels_count == 9:
		bot.send_message(message.chat.id, '9 лучших отелей:')
	start.bot_start(message)


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
