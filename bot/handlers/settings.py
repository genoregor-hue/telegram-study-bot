"""
Обработчики для настроек
"""
import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.settings_states import SettingsStates
from bot.keyboards.settings_kb import (
    get_settings_menu, get_language_keyboard, get_theme_keyboard, get_confirm_clear_keyboard
)
from bot.keyboards.main_menu import get_main_menu
from bot.utils.validators import validate_time
from bot.utils.logger import logger
import config

router = Router()
settings_db = f"{config.DB_PATH}/settings.db"


async def get_user_settings(user_id: int) -> dict:
    """Получение настроек пользователя"""
    try:
        async with aiosqlite.connect(settings_db) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM user_settings WHERE user_id = ?
            """, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                else:
                    # Создаем настройки по умолчанию
                    async with db.execute("""
                        INSERT INTO user_settings (user_id) VALUES (?)
                    """, (user_id,)) as insert_cursor:
                        await db.commit()
                    return {
                        "user_id": user_id,
                        "language": "ru",
                        "theme": "light",
                        "reminder_time": "08:00"
                    }
    except Exception as e:
        logger.error(f"Ошибка при получении настроек: {e}")
        return {
            "user_id": user_id,
            "language": "ru",
            "theme": "light",
            "reminder_time": "08:00"
        }


async def update_user_settings(user_id: int, **kwargs):
    """Обновление настроек пользователя"""
    try:
        updates = []
        params = []
        
        for key, value in kwargs.items():
            updates.append(f"{key} = ?")
            params.append(value)
        
        if not updates:
            return False
        
        params.append(user_id)
        
        async with aiosqlite.connect(settings_db) as db:
            await db.execute(f"""
                UPDATE user_settings
                SET {', '.join(updates)}
                WHERE user_id = ?
            """, params)
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении настроек: {e}")
        return False


@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: Message):
    """Меню настроек"""
    settings = await get_user_settings(message.from_user.id)
    
    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"🌐 Язык: {config.LANGUAGES.get(settings.get('language', 'ru'), 'Русский')}\n"
        f"🎨 Тема: {config.THEMES.get(settings.get('theme', 'light'), 'Светлая')}\n"
        f"⏰ Время напоминаний: {settings.get('reminder_time', '08:00')}\n\n"
        f"Выберите параметр для изменения:"
    )
    
    await message.answer(
        text,
        reply_markup=get_settings_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings_language")
async def settings_language(callback: CallbackQuery):
    """Выбор языка"""
    await callback.message.edit_text(
        "🌐 <b>Выбор языка</b>\n\nВыберите язык:",
        reply_markup=get_language_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("lang_"))
async def settings_language_set(callback: CallbackQuery):
    """Установка языка"""
    lang_code = callback.data.split("_")[1]
    success = await update_user_settings(callback.from_user.id, language=lang_code)
    
    if success:
        await callback.answer("✅ Язык изменен", show_alert=True)
        await settings_menu(callback.message)
    else:
        await callback.answer("❌ Ошибка при изменении языка", show_alert=True)


@router.callback_query(F.data == "settings_theme")
async def settings_theme(callback: CallbackQuery):
    """Выбор темы"""
    await callback.message.edit_text(
        "🎨 <b>Выбор темы</b>\n\nВыберите тему:",
        reply_markup=get_theme_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("theme_"))
async def settings_theme_set(callback: CallbackQuery):
    """Установка темы"""
    theme_code = callback.data.split("_")[1]
    success = await update_user_settings(callback.from_user.id, theme=theme_code)
    
    if success:
        await callback.answer("✅ Тема изменена", show_alert=True)
        await settings_menu(callback.message)
    else:
        await callback.answer("❌ Ошибка при изменении темы", show_alert=True)


@router.callback_query(F.data == "settings_reminder_time")
async def settings_reminder_time_start(callback: CallbackQuery, state: FSMContext):
    """Начало настройки времени напоминаний"""
    await state.set_state(SettingsStates.waiting_for_reminder_time)
    await callback.message.edit_text(
        "⏰ <b>Настройка времени напоминаний</b>\n\n"
        "Введите время в формате <b>HH:MM</b> (например, 08:00):",
        parse_mode="HTML"
    )


@router.message(SettingsStates.waiting_for_reminder_time)
async def settings_reminder_time_set(message: Message, state: FSMContext):
    """Установка времени напоминаний"""
    is_valid, error = validate_time(message.text)
    if not is_valid:
        await message.answer(f"❌ {error}\n\nПопробуйте снова:")
        return
    
    success = await update_user_settings(message.from_user.id, reminder_time=message.text)
    
    if success:
        await message.answer(
            f"✅ Время напоминаний установлено: {message.text}",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer("❌ Ошибка при установке времени.")
    
    await state.clear()


@router.callback_query(F.data == "settings_clear_data")
async def settings_clear_data_confirm(callback: CallbackQuery):
    """Подтверждение очистки данных"""
    await callback.message.edit_text(
        "⚠️ <b>Очистка данных</b>\n\n"
        "Вы уверены, что хотите удалить все ваши данные?\n"
        "Это действие нельзя отменить!",
        reply_markup=get_confirm_clear_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_clear")
async def settings_clear_data_execute(callback: CallbackQuery):
    """Выполнение очистки данных"""
    user_id = callback.from_user.id
    
    try:
        import aiosqlite
        from bot.database.schedule_model import delete_schedule_item
        from bot.database.homework_model import delete_homework
        from bot.database.notes_model import delete_note
        
        # Удаляем все данные пользователя
        async with aiosqlite.connect(config.SCHEDULE_DB) as db:
            await db.execute("DELETE FROM schedule WHERE user_id = ?", (user_id,))
            await db.commit()
        
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            await db.execute("DELETE FROM homework WHERE user_id = ?", (user_id,))
            await db.commit()
        
        async with aiosqlite.connect(config.NOTES_DB) as db:
            await db.execute("DELETE FROM notes WHERE user_id = ?", (user_id,))
            await db.commit()
        
        await callback.message.edit_text(
            "✅ Все данные успешно удалены!",
            reply_markup=get_settings_menu()
        )
        await callback.answer("✅ Данные удалены", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при очистке данных: {e}")
        await callback.answer("❌ Ошибка при удалении данных", show_alert=True)


@router.callback_query(F.data == "settings_back")
async def settings_back(callback: CallbackQuery):
    """Возврат в меню настроек"""
    await settings_menu(callback.message)
    await callback.answer()

