import re
from telebot.types import CallbackQuery

from loader import bot
from database import history


@bot.message_handler(commands=['history'])
def history_menu(message):
    bot.send_message(message.from_user.id, "Ваша история поиска:",
                     reply_markup=history.history_inline_keyboard(message.from_user.id))


@bot.callback_query_handler(func=lambda call: call.data.startswith('search:'))
def process_history_reply(call: CallbackQuery) -> None:
    """
    Функция, реагирующая на нажатие кнопки с выбором действия.

    :param call: отклик клавиатуры.
    """
    search_id = re.search(r'\d+', call.data).group()
    try:
        # with bot.retrieve_data(call.message.from_user.id, call.message.chat.id) as data:
        try:
            hotel_info, photo_info= history.show_history(search_id)
            # bot.send_media_group(call.message.chat.id, media=result)
        except ValueError:
            try:
                for hotel_info in history.show_history(search_id):
                    bot.send_message(call.message.chat.id, hotel_info, parse_mode="html")
            # re.findall(r'\[\[([^\]]+?)\]', text)
            except ValueError:
                message = history.history_get(call.message.from_user.id)
                bot.send_message(call.message.chat.id, text=message)
    except Exception:
        bot.send_message(call.message.chat.id, text='Не могу загрузить историю поиска:')
