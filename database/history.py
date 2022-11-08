import sqlite3 as sq
import os
from loader import bot
import datetime


database_path = os.path.join(os.path.abspath("database"), "bot_history.db")


def low_high_history_add(user_id, command, city, hotel_info, photo_count=None,
                         date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    try:
        with sq.connect(database_path) as con:
            cur = con.cursor()
            try:
                cur.execute("DELETE from bestdeal_history WHERE user_id = ?", (user_id,))
            except:
                pass
            if cur.execute("SELECT command, city, hotels_count, photo_count, date FROM history WHERE user_id = ?", (user_id,)).fetchone() == None:
                # converted_photo = convert_to_binary_data(hotel_photos)
                column_values = (user_id, command, city, hotel_info, photo_count, date)
                cur.execute("INSERT INTO history VALUES(?, ?, ?, ?, ?, ?)", column_values)
            else:
                try:
                    sqlite_update_query = """UPDATE history SET command = ?, city = ?, hotels_count = ?, photo_count = ?, date = ? where user_id = ?"""
                    column_values = (command, city, hotel_info, photo_count, date, user_id)
                    cur.execute(sqlite_update_query, column_values)
                except Exception:
                    print("Не удалось перезаписать {}".format(user_id))
            # cur.execute("DROP TABLE IF EXISTS history")
            # cur.execute("""CREATE TABLE IF NOT EXISTS history (
            # 	user_id TEXT PRIMARY KEY,
            # 	command TEXT,
            # 	city TEXT,
            # 	hotels_count TEXT,
            # 	hotels_photo BLOB,
            #     photo_count INTEGER,
            # 	date datetime
            # )""")
    except sq.Error as error:
        print("Ошибка при подключении к sqlite", error)


def best_history_add(user_id, command, city, min_price, max_price, min_distance, max_distance,
                     hotel_info, photo_count=None, date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    try:
        with sq.connect(database_path) as con:
            cur = con.cursor()
            try:
                cur.execute("DELETE FROM history WHERE user_id = ?", (user_id,))
            except:
                pass
            if cur.execute("SELECT command, city, min_price, max_price, min_distance, max_distance, hotels_count, \
            photo_count, date FROM bestdeal_history WHERE user_id = ?", (user_id,)).fetchone() == None:
                # converted_photo = convert_to_binary_data(hotel_photos)
                column_values = (user_id, command, city, min_price, max_price, min_distance,
                                 max_distance, hotel_info, photo_count, date)
                cur.execute("INSERT INTO bestdeal_history VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", column_values)
            else:
                try:
                    sqlite_update_query = """UPDATE bestdeal_history SET command = ?, city = ?, min_price = ?, max_price = ?,
                    min_distance = ?, max_distance = ?, hotels_count = ?, photo_count = ?, date = ? where user_id = ?"""
                    column_values = (command, city, min_price, max_price, min_distance,
                                 max_distance, hotel_info, photo_count, date, user_id)
                    cur.execute(sqlite_update_query, column_values)
                except Exception:
                    print("Не удалось перезаписать {}".format(user_id))
            # cur.execute("DROP TABLE IF EXISTS bestdeal_history")
            # cur.execute("""CREATE TABLE IF NOT EXISTS bestdeal_history (
            #     user_id TEXT PRIMARY KEY,
            #     command TEXT,
            #     city TEXT,
            #     min_price INTEGER,
            #     max_price INTEGER,
            #     min_distance INTEGER,
            #     max_distance INTEGER,
            #     hotels_count TEXT,
            #     photo_count INTEGER,
            #     date datetime
            # )""")
    except sq.Error as error:
        print("Ошибка при подключении к sqlite", error)
        # hotels_photo BLOB,

# def readphoto(photo):
# 	try:
# 		with open() as f:
# 			return f.read()
# 	except IOError as e:
# 		print(e)
# 		return False
# or
# def convert_to_binary_data(filename):
#     # Преобразование данных в двоичный формат
#     with open(filename, 'rb') as file:
#         blob_data = file.read()
#     return blob_data


# with sq.connect("bot_history.db") as con:
#     cur = con.cursor()
#     if cur.execute("SELECT command, hotels, date FROM history WHERE user_id = ?", ("3",)).fetchone() == None:
#     else:
#         row = cur.fetchone()
#         print(row)


@bot.message_handler(commands=['history'])
def history_get(message):
    try:
        with sq.connect(database_path) as con:
            cur = con.cursor()
            try:
                if (cur.execute("SELECT * FROM history WHERE user_id = ?", (message.from_user.id,)).fetchone() == None)\
                        and\
                        (cur.execute("SELECT * FROM bestdeal_history WHERE user_id = ?", (message.from_user.id,)).fetchone() == None):
                    print("Вы еще ничего не искали.")
                elif cur.execute("SELECT * FROM history WHERE user_id = ?", (message.from_user.id,)).fetchone() == None:
                    cur.execute("SELECT command, city, min_price, max_price, min_distance, max_distance,\
                                     hotels_count, photo_count, date FROM bestdeal_history WHERE user_id = ?",
                                (message.from_user.id,))
                    for res in cur:
                        command = res[0]
                        city = res[1]
                        min_price, max_price, min_distance, max_distance = res[2], res[3], res[4], res[5],
                        hotels_count = res[6]
                        if res[7] != None:
                            photo_count = res[7]
                        date = res[8]
                    # if 'photo_count' not in locals():
                    #     return command, city, min_price, max_price, min_distance, max_distance, hotels_count, date
                    # else:
                    #     return command, city, min_price, max_price, min_distance, max_distance, hotels_count, photo_count, date
                else:
                    cur.execute("SELECT command, city, hotels_count, photo_count, date FROM history WHERE user_id = ?",
                                (message.from_user.id,))
                    for res in cur:
                        command = res[0]
                        city = res[1]
                        hotels_count = res[2]
                        if res[3] != None:
                            photo_count = res[3]
                        date = res[4]
                        if 'photo_count' not in locals():
                            msg = "{}, {}, {}, {}".format(command, city, hotels_count, date)
                            # return command, city, hotels_count, date
                        else:
                            msg = "{}, {}, {}, {}, {}".format(command, city, hotels_count, photo_count, date)
                            # return command, city, hotels_count, photo_count, date
                        bot.send_message(message.chat.id, msg)

                # # row = cur.fetchone()
                # # return row
            except Exception as e:
                print("Не удалось загрузить историю user {}".format(message.from_user.id,), e)
    except sq.Error as error:
        print("Ошибка при подключении к sqlite", error)
if __name__ == '__main__':
    database_path = os.path.join(os.path.abspath("."), "bot_history.db")
