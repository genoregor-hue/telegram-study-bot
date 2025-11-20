"""
Состояния FSM для работы с заметками
"""
from aiogram.fsm.state import State, StatesGroup


class NotesStates(StatesGroup):
    """Состояния для создания/редактирования заметок"""
    waiting_for_title = State()
    waiting_for_content = State()
    editing_note = State()
    waiting_for_search = State()
    editing_title = State()
    editing_content = State()

