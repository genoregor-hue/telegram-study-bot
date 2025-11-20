"""
Обработчики для отображения прогресса
"""
from aiogram import Router, F
from aiogram.types import Message
from bot.keyboards.main_menu import get_main_menu
from bot.database.supabase_db import get_homework as supabase_get_homework
from bot.utils.formatters import format_progress_bar
from bot.utils.logger import logger

router = Router()


@router.message(F.text == "📊 Прогресс")
async def progress_menu(message: Message):
    """Отображение прогресса"""
    try:
        # Получаем все ДЗ из Supabase
        all_homework = await supabase_get_homework()
        total = len(all_homework)
        
        # В Supabase схеме нет поля is_completed, поэтому считаем все как невыполненные
        completed = 0
        pending = total
        percentage = 0.0
        
        if total > 0:
            # Можно считать выполненные по дате дедлайна (если дедлайн прошел)
            from datetime import date
            today = date.today()
            completed = len([h for h in all_homework if h.get('deadline') and 
                            (isinstance(h.get('deadline'), str) and 
                             date.fromisoformat(h.get('deadline')) < today or
                             (not isinstance(h.get('deadline'), str) and h.get('deadline') < today))])
            pending = total - completed
            percentage = (completed / total * 100) if total > 0 else 0
        
        progress_bar = format_progress_bar(percentage)
        
        text = (
            f"📊 <b>Ваш прогресс</b>\n\n"
            f"{progress_bar} {percentage:.1f}%\n\n"
            f"📘 Всего заданий: {total}\n"
            f"✅ Выполнено: {completed}\n"
            f"⏳ Осталось: {pending}\n\n"
        )
        
        # Дополнительная информация
        if percentage >= 80:
            text += "🎉 Отличная работа! Вы на правильном пути!"
        elif percentage >= 50:
            text += "👍 Хороший прогресс! Продолжайте в том же духе!"
        elif percentage > 0:
            text += "💪 Не сдавайтесь! Каждое задание важно!"
        else:
            text += "🚀 Начните выполнять задания, чтобы увидеть свой прогресс!"
        
        await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка при отображении прогресса: {e}")
        await message.answer("❌ Произошла ошибка при загрузке прогресса.", reply_markup=get_main_menu())

