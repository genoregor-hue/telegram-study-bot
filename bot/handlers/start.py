# Обработка команды /start
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.main_menu import get_main_menu
from bot.utils.logger import logger

router = Router()


@router.message(F.text.in_(["/start", "🔙 Главное меню"]))
async def cmd_start(message: Message, state: FSMContext):
    try:
        await state.clear()
        
        welcome_text = (
            "👋 <b>Добро пожаловать в бота для учебы!</b>\n\n"
            "Я помогу вам организовать учебный процесс:\n\n"
            "📅 <b>Расписание</b> - управление расписанием занятий\n"
            "📘 <b>Домашние задания</b> - отслеживание ДЗ и дедлайнов\n"
            "📝 <b>Заметки</b> - создание и хранение заметок\n"
            "⏰ <b>Напоминания</b> - напоминания о важных событиях\n"
            "📊 <b>Прогресс</b> - статистика выполнения заданий\n"
            "⚙️ <b>Настройки</b> - настройка бота\n\n"
            "Выберите раздел из меню ниже:"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
        logger.info(f"Пользователь {message.from_user.id} запустил бота")
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")


@router.message(F.text == "🔙 Главное меню")
async def back_to_menu(message: Message, state: FSMContext):
    await cmd_start(message, state)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    welcome_text = (
        "👋 <b>Добро пожаловать в бота для учебы!</b>\n\n"
        "Я помогу вам организовать учебный процесс:\n\n"
        "📅 <b>Расписание</b> - управление расписанием занятий\n"
        "📘 <b>Домашние задания</b> - отслеживание ДЗ и дедлайнов\n"
        "📝 <b>Заметки</b> - создание и хранение заметок\n"
        "⏰ <b>Напоминания</b> - напоминания о важных событиях\n"
        "📊 <b>Прогресс</b> - статистика выполнения заданий\n"
        "⚙️ <b>Настройки</b> - настройка бота\n\n"
        "Выберите раздел из меню ниже:"
    )
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.message.answer(
        "Главное меню:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

