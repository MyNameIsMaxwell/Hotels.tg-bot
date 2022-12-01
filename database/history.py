import os
import sqlite3 as sq
import datetime
from loguru import logger
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Tuple

database_path = os.path.join(os.path.abspath("database"), "bot_history.db")


@logger.catch()
def database_create() -> None:
	"""
	Функция создающая базы данных с таблицами users и history, если их нет.
	Таблица users хранит информацию об id пользователей.
	Таблица history хранит в текстовом виде информацию об отелях, фотографиях и ссылку на id пользователя.
	"""
	try:
		with sq.connect(database_path) as con:
			cur = con.cursor()
			cur.execute("""CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id TEXT UNIQUE NOT NULL
            )""")
			cur.execute("""CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                command TEXT NOT NULL,
                hotel_info TEXT NOT NULL,
                photo_urls TEXT DEFAULT NULL,
                date datetime
            )""")
	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


@logger.catch()
def show_history(search_id: str):
	"""
	Функция получающая id записи таблицы history в БД и возвращающая информацию об отеле и ссылки на фото, если они имеются.
	:param search_id:
	:return: hotel_info, photo_info: (Union[str, str]) информацию об отеле и ссылки на фото, если они имеются.
	:return: hotel_info: (str) информацию об отеле, если фотографий не имеется.
	"""
	try:
		with sq.connect(database_path) as con:
			cur = con.cursor()
			result = cur.execute("""SELECT hotel_info, photo_urls FROM history
									WHERE id = ?""", (search_id,)).fetchone()

			if len(result) == 0:
				return "История пуста"
			hotel_info = result[0]
			if result[1] is not None:
				photo_info = result[1]
			if 'photo_info' in locals():
				yield hotel_info, photo_info
			else:
				yield hotel_info
	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


@logger.catch()
def history_inline_keyboard(user_id) -> InlineKeyboardMarkup:
	"""
	Клавиатура с кнопками - выбор действия с историей поиска.
	:param user_id: (int) id пользователя, который проводит поиск истории.
	:return: клавиатура InlineKeyboardMarkup
	"""
	keyboard = InlineKeyboardMarkup(row_width=1)
	try:
		for searching_id, command, hotel_info, photo_info, date_info in history_get(user_id):
			keyboard.add(
				InlineKeyboardButton(text=f'{command} - {date_info}', callback_data=f'search:{searching_id}')
			)
	except ValueError:
		try:
			for searching_id, command, hotel_info, date_info in history_get(user_id):
				keyboard.add(
					InlineKeyboardButton(text=f'{command} - {date_info}', callback_data=f'search:{searching_id}')
				)
		except ValueError:
			keyboard.add(
				InlineKeyboardButton(text="История поиска пуста. Введите /help")
			)

	return keyboard


@logger.catch()
def history_get(user_id: int) -> Tuple:
	"""
	Функция, которая выводит название команды и времени поиска для инлайн клавиатуры.
	:param user_id: (int) id пользователя, который проводит поиск истории.
	:return: info: (tuple) кортеж с информацией об истории поиска, без текста и фотографий.
	"""
	try:
		with sq.connect(database_path) as con:
			cur = con.cursor()
			try:
				try:
					cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
				except Exception as exp:
					if exp.args[0] == 'UNIQUE constraint failed: users.user_id':
						pass
				result = cur.execute("""SELECT h.id, h.command, h.hotel_info, h.photo_urls, h.date FROM history as h 
										JOIN users ON users.id=h.user_id WHERE users.user_id = ?""",
									 (user_id,)).fetchall()
				if len(result) > 3:
					cur.execute("""DELETE FROM history WHERE id = ?""", (result[0][0],))
					result = cur.execute("""SELECT h.id, h.command, h.hotel_info, h.photo_urls, h.date FROM history as h 
											JOIN users ON users.id=h.user_id WHERE users.user_id = ?""",
										 (user_id,)).fetchall()

				for info in result:
					if info[2] is not None:
						yield info
					else:
						info = list(info)
						del info[2]
						yield info
			except Exception as exp:
				print(exp)
	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


@logger.catch()
def history_add(user_id: int, command: str, hotel_info: str, photos: str = None,
				date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) -> None:
	"""
	Функция, добавляющая запись с информацией о команде, которую использовал пользователь, отеле, фотографиях и дате
	поиска в базу данных.
	Проверяет есть ли пользователь в таблице users БД, если нет, то добавляет.
	Если количество отелей в поиске пользователя больше трёх, то тот, который искался раньше всех.
	:param user_id: (int) id пользователя.
	:param command: (str) команда, по которой пользователь искал информацию.
	:param hotel_info: (str) информация об отеле в виде строки.
	:param photos: (str) url фотографий в виде строки.
	:param date: (date) дата и время поиска.
	"""
	try:
		with sq.connect(database_path) as con:
			cur = con.cursor()
			try:
				cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
			except Exception as exp:
				if exp.args[0] == 'UNIQUE constraint failed: users.user_id':
					pass
			table_user_id = cur.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
			for value in table_user_id:
				table_user_id = value[0]
			count_notes = cur.execute("""SELECT id FROM history WHERE user_id = ?""", (table_user_id,)).fetchall()
			if len(count_notes) > 3:
				cur.execute("""DELETE FROM history WHERE id = ?""", (count_notes[0][0],))
			column_values = (table_user_id, command, hotel_info, photos, date)
			cur.execute("""INSERT INTO history (user_id, command, hotel_info, photo_urls, date) 
                            VALUES(?, ?, ?, ?, ?)""", column_values)
	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


@logger.catch()
def delete_db():
	"""Функция удаляющая таблицы из БД"""
	try:
		with sq.connect(database_path) as con:
			cur = con.cursor()
			cur.execute("DROP TABLE IF EXISTS history")
			cur.execute("DROP TABLE IF EXISTS users")
	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


database_create()
if __name__ == '__main__':
	database_path = os.path.join(os.path.abspath("."), "bot_history.db")
