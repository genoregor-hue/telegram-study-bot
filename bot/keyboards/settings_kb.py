"""
Клавиатуры для настроек
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config


def get_settings_menu() -> InlineKeyboardMarkup:
    """Меню настроек"""
    keyboard = [
        [InlineKeyboardButton(text="🌐 Язык", callback_data="settings_language")],
        [InlineKeyboardButton(text="🎨 Тема", callback_data="settings_theme")],
        [InlineKeyboardButton(text="⏰ Время напоминаний", callback_data="settings_reminder_time")],
        [InlineKeyboardButton(text="🗑️ Очистить данные", callback_data="settings_clear_data")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Выбор языка"""
    keyboard = []
    for lang_code, lang_name in config.LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(
            text=lang_name,
            callback_data=f"lang_{lang_code}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="settings_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_theme_keyboard() -> InlineKeyboardMarkup:
    """Выбор темы"""
    keyboard = []
    for theme_code, theme_name in config.THEMES.items():
        keyboard.append([InlineKeyboardButton(
            text=theme_name,
            callback_data=f"theme_{theme_code}"
        )])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="settings_back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirm_clear_keyboard() -> InlineKeyboardMarkup:
    """Подтверждение очистки данных"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Да, очистить", callback_data="confirm_clear")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="settings_back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

