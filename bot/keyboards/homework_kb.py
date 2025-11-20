"""
Клавиатуры для работы с домашними заданиями
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_homework_menu() -> InlineKeyboardMarkup:
    """Меню домашних заданий"""
    keyboard = [
        [InlineKeyboardButton(text="➕ Добавить ДЗ", callback_data="homework_add")],
        [InlineKeyboardButton(text="📅 На сегодня", callback_data="homework_today")],
        [InlineKeyboardButton(text="📆 На неделю", callback_data="homework_week")],
        [InlineKeyboardButton(text="🔍 По предмету", callback_data="homework_by_subject")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="homework_edit")],
        [InlineKeyboardButton(text="✅ Отметить выполненным", callback_data="homework_complete")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data="homework_delete")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_homework_items_keyboard(items: List[Dict[str, Any]], action: str = "select") -> InlineKeyboardMarkup:
    """Клавиатура со списком ДЗ"""
    keyboard = []
    for item in items:
        subject = item.get('subject', '')
        task = item.get('task', '')[:30] + "..." if len(item.get('task', '')) > 30 else item.get('task', '')
        item_id = item.get('id')
        is_completed = item.get('is_completed', 0)
        status = "✅" if is_completed else "⏳"
        keyboard.append([InlineKeyboardButton(
            text=f"{status} {subject}: {task}",
            callback_data=f"{action}_homework_{item_id}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="homework_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_edit_homework_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для редактирования ДЗ"""
    keyboard = [
        [InlineKeyboardButton(text="✏️ Предмет", callback_data=f"edit_homework_subject_{item_id}")],
        [InlineKeyboardButton(text="📝 Задание", callback_data=f"edit_homework_task_{item_id}")],
        [InlineKeyboardButton(text="📅 Дедлайн", callback_data=f"edit_homework_deadline_{item_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="homework_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

