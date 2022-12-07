# -*- coding: windows-1251 -*-
from telebot.handler_backends import State, StatesGroup


class LowHighStates(StatesGroup):
	"""
	Класс реализует состояние пользователя внутри сценариев.

	Attributes:
		city(State): город, в котором ищем отели.
		hotels_count(State): количество выводимых отелей.
		load_photo(State): вывод с фотографиями или без.
		photo_count(State): количество фотографий выводимого отеля.
		price_to(State): максимально возможная цена за ночь в отеле.
		dist_from_center(State): максимально возможная дистанция от города .
	"""
	city = State()
	hotels_count = State()
	load_photo = State()
	photo_count = State()
	price_to = State()
	dist_from_center = State()
