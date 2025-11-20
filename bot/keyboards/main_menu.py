"""
Главное меню бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """
    Создание главного меню
    
    Returns:
        ReplyKeyboardMarkup: Клавиатура главного меню
    """
    keyboard = [
        [KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="📘 Домашние задания")],
        [KeyboardButton(text="📝 Заметки")],
        [KeyboardButton(text="⏰ Напоминания")],
        [KeyboardButton(text="📊 Прогресс")],
        [KeyboardButton(text="⚙️ Настройки")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

