from telebot.handler_backends import State, StatesGroup


class MyStatesLowprice(StatesGroup):
	"""
	Класс реализует состояние пользователя внутри сценария lowprice.

	Attributes:
		city_lowprice(State): город, в котором ищем отели.
		hotels_count_lowprice(State): количество выводимых отелей.
		load_photo_lowprice(State): вывод с фотографиями или без.
		photo_count_lowprice(State): количество фотографий выводимого отеля.
	"""
	city_lowprice = State()
	hotels_count_lowprice = State()
	load_photo_lowprice = State()
	photo_count_lowprice = State()


class MyStatesHighprice(StatesGroup):
	"""
	Класс реализует состояние пользователя внутри сценария highprice.

	Attributes:
		city_highprice(State): город, в котором ищем отели.
		hotels_count_highprice(State): количество выводимых отелей.
		load_photo_highprice(State): вывод с фотографиями или без.
		photo_count_highprice(State): количество фотографий выводимого отеля.
	"""
	city_highprice = State()
	hotels_count_highprice = State()
	load_photo_highprice = State()
	photo_count_highprice = State()


class MyStatesBestdeal(StatesGroup):
	"""
	Класс реализует состояние пользователя внутри сценария bestdeal.

	Attributes:
		city_bestdeal(State): город, в котором ищем отели.
		price_to_bestdeal(State): максимально возможная цена за ночь в отеле.
		dist_from_center_to_bestdeal(State): максимально возможная дистанция от города .
		hotels_count_bestdeal(State): количество выводимых отелей.
		load_photo_bestdeal(State): вывод с фотографиями или без.
		photo_count_bestdeal(State): количество фотографий выводимого отеля.
	"""
	city_bestdeal = State()
	price_to_bestdeal = State()
	dist_from_center_from_bestdeal = State()
	dist_from_center_to_bestdeal = State()
	hotels_count_bestdeal = State()
	load_photo_bestdeal = State()
	photo_count_bestdeal = State()
