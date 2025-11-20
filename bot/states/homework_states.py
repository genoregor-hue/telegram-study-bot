"""
Состояния FSM для работы с домашними заданиями
"""
from aiogram.fsm.state import State, StatesGroup


class HomeworkStates(StatesGroup):
    """Состояния для добавления/редактирования ДЗ"""
    waiting_for_subject = State()
    waiting_for_task = State()
    waiting_for_deadline = State()
    editing_item = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()

