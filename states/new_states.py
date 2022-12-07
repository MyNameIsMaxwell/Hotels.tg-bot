# -*- coding: windows-1251 -*-
from telebot.handler_backends import State, StatesGroup


class LowHighStates(StatesGroup):
	"""
	����� ��������� ��������� ������������ ������ ���������.

	Attributes:
		city(State): �����, � ������� ���� �����.
		hotels_count(State): ���������� ��������� ������.
		load_photo(State): ����� � ������������ ��� ���.
		photo_count(State): ���������� ���������� ���������� �����.
		price_to(State): ����������� ��������� ���� �� ���� � �����.
		dist_from_center(State): ����������� ��������� ��������� �� ������ .
	"""
	city = State()
	hotels_count = State()
	load_photo = State()
	photo_count = State()
	price_to = State()
	dist_from_center = State()
