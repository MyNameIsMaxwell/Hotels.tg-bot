import re
from telebot.types import CallbackQuery, InputMediaPhoto
from loguru import logger

from handlers import start
from loader import bot
from database import history


@bot.message_handler(commands=['history'])
@logger.catch()
def history_menu(message):
    """Функция, реагирующая на команду 'history' и показывает клавиатуру с последними тремя запросами пользователя."""
    bot.send_message(message.from_user.id, "Ваша история поиска:",
                     reply_markup=history.history_inline_keyboard(message.from_user.id))


@bot.callback_query_handler(func=lambda call: call.data.startswith('search:'))
@logger.catch()
def process_history_reply(call: CallbackQuery) -> None:
    """
    Функция, реагирующая на нажатие кнопки при выборе истории запросов.
    call.data хранит id записи выбранного варианта, который потом передает в функцию show_history, где, после ответа от
    БД, получает информацию об отелях и фотографиях, обрабатывает ответ с помощью регулярных выражений и выводит результат
    в чат с помощью InputMediaPhoto.
    Если фотографий не было, то выдает ошибку ValueError, которая обрабатывается и вызывает функцию show_history, где,
    после ответа от БД, получает информацию об отелях, обрабатывает ответ с помощью регулярных выражений и выводит
    результат с помощью send_message.


    :param call: отклик клавиатуры.
    """

    search_id = re.search(r'\d+', call.data).group()
    try:
        try:
            for hotel_info, photo_info in history.show_history(search_id):
                index = 0
                hotels_list = re.findall(r"\[\'([^\[\]]+)\'\]", hotel_info.replace('"', "'"), flags=re.DOTALL)
                photo_list = re.findall(r"\[\'([^\[\]]+)\'\]", photo_info.replace('"', "'"), flags=re.DOTALL)
                for info in hotels_list:
                    text = info.replace("\\n", "\n")
                    if len(photo_list[index].split(",")) < 3:
                        photos = [photo_list[index].replace("'", "").replace(" ", "")]
                    else:
                        photos = photo_list[index].replace("'", "").replace(" ", "").split(",")
                    result = [InputMediaPhoto(media=url, caption=text) if index == 0
                                else InputMediaPhoto(media=url) for index, url in enumerate(photos)]
                    bot.send_media_group(call.message.chat.id, media=result)
                    index += 1
        except ValueError:
            try:
                for hotel_info in history.show_history(search_id):
                    hotels_list = re.findall(r"\[\'([^\[\]]+)\'\]", hotel_info.replace('"', "'"), flags=re.DOTALL)
                    for info in hotels_list:
                        bot.send_message(call.message.chat.id, info.replace("\\n", "\n"), parse_mode="html")
            except ValueError:
                message = history.history_get(call.message.from_user.id)
                bot.send_message(call.message.chat.id, text=message)
        start.bot_start(call.message)
    except Exception as exp:
        print(exp)
        bot.send_message(call.message.chat.id, text='Не могу загрузить историю поиска:')
