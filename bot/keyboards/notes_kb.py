"""
Клавиатуры для работы с заметками
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict, Any


def get_notes_menu() -> InlineKeyboardMarkup:
    """Меню заметок"""
    keyboard = [
        [InlineKeyboardButton(text="➕ Создать заметку", callback_data="notes_add")],
        [InlineKeyboardButton(text="📋 Все заметки", callback_data="notes_all")],
        [InlineKeyboardButton(text="🔍 Поиск", callback_data="notes_search")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="notes_edit")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data="notes_delete")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_notes_list_keyboard(notes: List[Dict[str, Any]], action: str = "select") -> InlineKeyboardMarkup:
    """Клавиатура со списком заметок"""
    keyboard = []
    for note in notes:
        title = note.get('title', 'Без названия')
        note_id = note.get('id')
        keyboard.append([InlineKeyboardButton(
            text=title,
            callback_data=f"{action}_note_{note_id}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="notes_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_note_actions_keyboard(note_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий с заметкой"""
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_note_{note_id}")],
        [InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_note_{note_id}")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="notes_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

