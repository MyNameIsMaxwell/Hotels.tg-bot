import sqlite3 as sq
import os
import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

database_path = os.path.join(os.path.abspath("database"), "bot_history.db")


def database_create():
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


def show_history(search_id):
	try:
		with sq.connect(database_path) as con:
			cur = con.cursor()
			result = cur.execute("""SELECT hotel_info, photo_urls FROM history
									WHERE id = ?""", (search_id,)).fetchone()

			if len(result) == 0:
				return "История пуста"
			for info in result:

				hotel_info = info[0]
				if info[1] is not None:
					photo_info = info[1]
				if 'photo_info' in locals():
					yield hotel_info, photo_info
				else:
					yield hotel_info


	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


def history_inline_keyboard(user_id):
	"""
	Клавиатура с кнопками - выбор действия с историей поиска.
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
			return 'Вы пока что ничего не искали'

	return keyboard


def history_get(user_id):
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
										JOIN users ON users.id=h.user_id WHERE users.user_id = ?""", (user_id,)).fetchall()
				if len(result) > 3:
					cur.execute("""DELETE FROM history WHERE id = ?""", (result[0][0],))
					result = cur.execute("""SELECT h.id, h.command, h.hotel_info, h.photo_urls, h.date FROM history as h 
											JOIN users ON users.id=h.user_id WHERE users.user_id = ?""", (user_id,)).fetchall()

				for info in result:
					if info[2] is not None:
						yield info
					else:
						info = list(info)
						del info[2]
						yield info
					# command = info[0]
					# hotel_info = info[1]
					# if info[2] is not None:
					# 	photo_info = info[2]
					# date_info = info[3]
					# if 'photo_info' in locals():
					# 	yield command, hotel_info, photo_info, date_info
					# else:
					# 	yield command, hotel_info, date_info
			except Exception as exp:
				print(exp)


	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


def history_add(user_id, command, hotel_info, photos=None, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
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
			cur.execute("""INSERT INTO history (user_id, command, hotel_info,photo_urls, date) 
                            VALUES(?, ?, ?, ?, ?)""", column_values)
	except sq.Error as error:
		print("Ошибка при подключении к sqlite", error)


def delete_db():
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
	database_create()

