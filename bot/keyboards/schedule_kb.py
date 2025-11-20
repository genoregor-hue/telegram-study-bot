"""
Клавиатуры для работы с расписанием
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_schedule_menu() -> InlineKeyboardMarkup:
    """Меню расписания"""
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить предмет", callback_data="schedule_add")],
        [InlineKeyboardButton(text="📅 Просмотр на день", callback_data="schedule_day")],
        [InlineKeyboardButton(text="📆 Просмотр на неделю", callback_data="schedule_week")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="schedule_edit")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data="schedule_delete")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_days_keyboard() -> InlineKeyboardMarkup:
    """Выбор дня недели"""
    days = [
        ("Понедельник", 0),
        ("Вторник", 1),
        ("Среда", 2),
        ("Четверг", 3),
        ("Пятница", 4),
        ("Суббота", 5),
        ("Воскресенье", 6)
    ]
    keyboard = []
    for day_name, day_num in days:
        keyboard.append([InlineKeyboardButton(
            text=day_name,
            callback_data=f"day_{day_num}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="schedule_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_schedule_items_keyboard(items: List[Dict[str, Any]], action: str = "select") -> InlineKeyboardMarkup:
    """Клавиатура со списком предметов"""
    keyboard = []
    for item in items:
        subject = item.get('subject', '')
        time = item.get('time', '')
        item_id = item.get('id')
        keyboard.append([InlineKeyboardButton(
            text=f"{time} - {subject}",
            callback_data=f"{action}_schedule_{item_id}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="schedule_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_edit_schedule_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования предмета"""
    keyboard = [
        [InlineKeyboardButton(text="✏️ Предмет", callback_data=f"edit_schedule_subject_{item_id}")],
        [InlineKeyboardButton(text="🕐 Время", callback_data=f"edit_schedule_time_{item_id}")],
        [InlineKeyboardButton(text="🚪 Кабинет", callback_data=f"edit_schedule_room_{item_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="schedule_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

