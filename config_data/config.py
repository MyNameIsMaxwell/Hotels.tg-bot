import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv('.env.template'):
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv('.env.template')

BOT_TOKEN = os.getenv('BOT_TOKEN')
headers = {
    "RAPID_API_KEY": os.getenv('RAPID_API_KEY'),
    "RAPID_API_HOST": "hotels4.p.rapidapi.com"
}
DEFAULT_COMMANDS = (
    ('lowprice', "Узнать топ самых дешёвых отелей в городе"),
    ('highprice', "Узнать топ самых дорогих отелей в городе"),
    ('bestdeal', "Узнать топ отелей, наиболее подходящих по цене и расположению от центра"),
    ('history', "Узнать историю поиска отелей "),
    ('help', "Вывести справку")
)
