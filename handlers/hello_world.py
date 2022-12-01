from loader import bot


@bot.message_handler(commands=['hello-world'])
def hello_message(message):
	"""
	Функция, реагирующая на команду 'hello-world'.

	:param message: сообщение Telegram
	"""
	bot.reply_to(message, f"Привет, <i>{message.from_user.first_name}</i> ✌", parse_mode='HTML')
