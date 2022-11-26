from loader import bot
from handlers import *


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	if message.text == "Lowprice" or message.text == '/lowprice' or message.text == 'lowprice' or message.text == 'Lowprice💸':
		lowprice.lowprice_menu(message)
	elif message.text == "Highprice" or message.text == '/highprice' or message.text == 'highprice' or message.text == 'Highprice🏢' :
		highprice.highprice_menu(message)
	elif message.text == "Bestdeal" or message.text == '/bestdeal' or message.text == 'bestdeal' or message.text == 'Bestdeal☑️':
		bestdeal.bestdeal_menu(message)
	elif message.text == "History" or message.text == '/history' or message.text == 'history' or message.text == 'History🕰':
		history_button.history_menu(message)
	elif message.text == "Привет" or message.text == "привет":
		bot.send_message(message.from_user.id, "Привет, нажми <i>/help</i> и посмотри, чем я могу тебе помочь?", parse_mode='HTML')