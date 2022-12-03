from telebot import TeleBot
from loguru import logger
from telebot.storage import StateMemoryStorage
from config_data import config


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
api_headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
logger.add(config.LOG_PATH, format="{time} - {level} - {message}", level="DEBUG", rotation="10 MB", compression="zip")
