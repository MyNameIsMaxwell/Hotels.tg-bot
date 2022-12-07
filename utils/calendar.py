# -*- coding: windows-1251 -*-
from datetime import date, timedelta
from telegram_bot_calendar import DetailedTelegramCalendar

from loader import bot
from handlers import handler


def calendar_in(message):
	"""
	�������, ����������� �� ������� ������ �� ����������-��������� � ���� ������.
	������� ���������: ����������� ������� ������ ���� - ������, ������������ - ��� ����.
	:param message: ��������� Telegram
	"""
	calendar, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
											  max_date=date.today() + timedelta(days=730), locale='ru',
											  calendar_id="in").build()
	bot.send_message(message.chat.id,
					 f"������� ���� ������:",
					 reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id="in"))
def calendar_in_2(call) -> None:
	"""
	�������, ����������� �� ������� ������ �� ����������-��������� � ���� ������.
	������� ���������: ����������� ������� ������ ���� - ������, ������������ - ��� ����.
	�������� ���������� ������ � ���� ������ ��� ���������� ���������.

	:param call: ������ ����������.
	"""
	result, key, step = DetailedTelegramCalendar(min_date=date.today() + timedelta(days=1),
												 max_date=date.today() + timedelta(days=730), locale='ru',
												 calendar_id="in").process(call.data)
	if not result and key:
		bot.edit_message_text(f"���� ������:",
							  call.message.chat.id,
							  call.message.message_id,
							  reply_markup=key)
	elif result:
		bot.edit_message_text(f"���� ������: {result}",
							  call.message.chat.id,
							  call.message.message_id)

	if result is not None:
		with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
			data['dateIn'] = result
		calendar_out(call.message)


def calendar_out(message):
	"""
	�������, ����������� �� ������� ������ �� ����������-��������� � ���� ������.
	������� ���������: ����������� ������� ������ ���� - �� ��������� ���� ����� ���� ������,
	������������ - ��� ���� �� ���� ������.
	:param message: ��������� Telegram
	"""
	with bot.retrieve_data(message.chat.id, message.chat.id) as data:
		calendar, step = DetailedTelegramCalendar(min_date=data['dateIn'] + timedelta(days=1),
												  max_date=data['dateIn'] + timedelta(days=730), locale='ru',
												  calendar_id="out").build()
	bot.send_message(message.chat.id,
					 f"���� ������:",
					 reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id="out"))
def calendar_out_2(call) -> None:
	"""
		�������, ����������� �� ������� ������ �� ����������-��������� � ���� ������.
		������� ���������: ����������� ������� ������ ���� - �� ��������� ���� ����� ���� ������,
		������������ - ��� ���� �� ���� ������.
		�������� ���������� ������ � ���� ������ ��� ���������� ���������.
		�������� �������, ����������� �������� ��������� ������ �� ��������� ������, ���������� �� ������������.

		:param call: ������ ����������.
		"""
	with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
		result, key, step = DetailedTelegramCalendar(min_date=data['dateIn'] + timedelta(days=1),
													 max_date=data['dateIn'] + timedelta(days=730), locale='ru',
													 calendar_id="out").process(call.data)
	if not result and key:
		bot.edit_message_text(f"���� ������:",
							  call.message.chat.id,
							  call.message.message_id,
							  reply_markup=key)
	elif result:
		bot.edit_message_text(f"���� ������: {result}",
							  call.message.chat.id,
							  call.message.message_id)

		with bot.retrieve_data(call.message.chat.id, call.message.chat.id) as data:
			data['dateOut'] = result
		handler.ready_for_answer(call.message)
		bot.delete_state(call.message.chat.id, call.message.chat.id)
