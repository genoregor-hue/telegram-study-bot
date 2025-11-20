# Обработка напоминаний
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta
from bot.keyboards.main_menu import get_main_menu
from bot.utils.reminder_scheduler import (
    add_daily_reminder, add_one_time_reminder, get_user_reminders
)
from bot.utils.validators import validate_time, validate_date
from bot.utils.logger import logger
from bot.database.supabase_db import get_schedule as supabase_get_schedule, get_homework as supabase_get_homework
from datetime import date as date_type

router = Router()


async def send_reminder_message(bot, user_id: int, text: str):
    try:
        await bot.send_message(user_id, f"⏰ <b>Напоминание</b>\n\n{text}", parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка при отправке напоминания: {e}")


@router.message(F.text == "⏰ Напоминания")
async def reminders_menu(message: Message):
    text = (
        "⏰ <b>Напоминания</b>\n\n"
        "Я могу напомнить вам о:\n\n"
        "📅 О предстоящих парах\n"
        "📘 О дедлайнах домашних заданий\n"
        "💬 О ваших личных напоминаниях\n\n"
        "Напоминания о парах и ДЗ настраиваются автоматически.\n"
        "Для настройки времени напоминаний перейдите в ⚙️ Настройки."
    )
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")


async def setup_schedule_reminders(bot, user_id: int, reminder_time: str = "08:00"):
    try:
        today = datetime.now().date()
        
        # Получаем расписание на сегодня
        schedule_list = await supabase_get_schedule(date=today)
        
        if schedule_list:
            # Сортируем по времени
            schedule_sorted = sorted(schedule_list, key=lambda x: x.get('time', ''))
            first_class = schedule_sorted[0]
            class_time = first_class.get('time', '')
            subject = first_class.get('subject', '')
            
            # Вычисляем время напоминания (за 30 минут до первой пары)
            hour, minute = map(int, class_time.split(':'))
            reminder_datetime = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            reminder_datetime -= timedelta(minutes=30)
            
            if reminder_datetime > datetime.now():
                text = f"📅 Через 30 минут пара: {subject} в {class_time}"
                await add_one_time_reminder(
                    user_id,
                    reminder_datetime,
                    send_reminder_message,
                    bot,
                    text
                )
    except Exception as e:
        logger.error(f"Ошибка при настройке напоминаний о парах: {e}")


async def setup_homework_reminders(bot, user_id: int):
    try:
        homework_list = await supabase_get_homework()
        today = datetime.now().date()
        
        for item in homework_list:
            deadline_str = item.get('deadline')
            if not deadline_str:
                continue
            
            if isinstance(deadline_str, str):
                deadline_date = date_type.fromisoformat(deadline_str)
            else:
                deadline_date = deadline_str
            
            # Напоминание за день до дедлайна
            reminder_date = deadline_date - timedelta(days=1)
            if reminder_date >= today:
                reminder_datetime = datetime.combine(reminder_date, datetime.min.time().replace(hour=9, minute=0))
                
                if reminder_datetime > datetime.now():
                    subject = item.get('subject', '')
                    task = item.get('hw', '')
                    text = f"📘 Завтра дедлайн по {subject}: {task}"
                    await add_one_time_reminder(
                        user_id,
                        reminder_datetime,
                        send_reminder_message,
                        bot,
                        text
                    )
    except Exception as e:
        logger.error(f"Ошибка при настройке напоминаний о ДЗ: {e}")

