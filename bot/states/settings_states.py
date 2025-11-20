"""
Состояния FSM для настроек
"""
from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    """Состояния для настроек"""
    waiting_for_reminder_time = State()

