from loader import bot
from handlers import *


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	if message.text == "Lowprice" or message.text == '/lowprice':
		lowprice.lowprice_menu(message)
	elif message.text == "Highprice" or message.text == '/highprice':
		highprice.highprice_menu(message)
	elif message.text == "Bestdeal" or message.text == '/bestdeal':
		bestdeal.bestdeal_menu(message)
	elif message.text == "History" or message.text == '/history':
		history.history_menu(message)
	elif message.text == "Привет":
		bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")