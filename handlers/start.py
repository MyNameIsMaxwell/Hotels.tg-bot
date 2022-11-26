from telebot import types

from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
    item1 = types.KeyboardButton("Lowprice💸")
    item2 = types.KeyboardButton('Highprice🏢')
    item3 = types.KeyboardButton("Bestdeal☑️")
    item4 = types.KeyboardButton("History🕰")
    markup.row(item1, item2, item3)
    markup.row(item4)
    bot.send_message(message.chat.id, 'Выберите вариант:', reply_markup=markup)

