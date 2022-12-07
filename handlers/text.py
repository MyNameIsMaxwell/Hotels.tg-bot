from loader import bot
from handlers import *
from loguru import logger


@bot.message_handler(content_types=['text'])
@logger.catch()
def get_text_messages(message):
	"""
	Функция, реагирующая на возможные варианты ввода пользователем желаемого варианта
	для поиска,	и вызывающая функцию для начала поиска в данной категории.

	:param message: сообщение Telegram
	"""
	if message.text == "Lowprice" or message.text == '/lowprice' or message.text == 'lowprice' or message.text == 'Lowprice💸':
		bot.send_message(message.chat.id, 'Давай узнаем топ самых дешёвых отелей в городе!\nКакой город?')
		handler.command_get(message, "lowprice")
	elif message.text == "Highprice" or message.text == '/highprice' or message.text == 'highprice' or message.text == 'Highprice🏢' :
		bot.send_message(message.chat.id, "Давай узнаем топ самых дорогих отелей в городе!\nКакой город?")
		handler.command_get(message, "highprice")
	elif message.text == "Bestdeal" or message.text == '/bestdeal' or message.text == 'bestdeal' or message.text == 'Bestdeal☑️':
		bot.send_message(message.chat.id, 'Давай подберем подходящий отель!\nКакой город?')
		handler.command_get(message, "bestdeal")
	elif message.text == "History" or message.text == '/history' or message.text == 'history' or message.text == 'History🕰':
		history_button.history_menu(message)
	elif message.text == "Привет" or message.text == "привет":
		bot.send_message(message.from_user.id, "Привет, нажми <i>/help</i> и посмотри, чем я могу тебе помочь?", parse_mode='HTML')