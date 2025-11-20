"""
Состояния FSM для работы с расписанием
"""
from aiogram.fsm.state import State, StatesGroup


class ScheduleStates(StatesGroup):
    """Состояния для добавления/редактирования расписания"""
    waiting_for_subject = State()
    waiting_for_time = State()
    waiting_for_room = State()
    waiting_for_day = State()
    editing_item = State()
    waiting_for_edit_field = State()
    waiting_for_edit_value = State()

