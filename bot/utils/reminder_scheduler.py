"""
Модуль для работы с напоминаниями через apscheduler
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from typing import Callable, Any
from bot.utils.logger import logger

# Глобальный планировщик
scheduler = AsyncIOScheduler()


def start_scheduler():
    """Запуск планировщика"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Планировщик напоминаний запущен")


def stop_scheduler():
    """Остановка планировщика"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Планировщик напоминаний остановлен")


async def add_daily_reminder(user_id: int, time: str, callback: Callable, *args, **kwargs):
    """
    Добавление ежедневного напоминания
    
    Args:
        user_id: ID пользователя
        time: Время в формате HH:MM
        callback: Функция обратного вызова
        *args, **kwargs: Аргументы для callback
    """
    try:
        hour, minute = map(int, time.split(':'))
        job_id = f"daily_reminder_{user_id}_{time}"
        
        trigger = CronTrigger(hour=hour, minute=minute)
        scheduler.add_job(
            callback,
            trigger=trigger,
            id=job_id,
            args=[user_id, *args],
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"Добавлено ежедневное напоминание для пользователя {user_id} в {time}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении ежедневного напоминания: {e}")


async def add_one_time_reminder(user_id: int, reminder_time: datetime, callback: Callable, *args, **kwargs):
    """
    Добавление одноразового напоминания
    
    Args:
        user_id: ID пользователя
        reminder_time: Время напоминания
        callback: Функция обратного вызова
        *args, **kwargs: Аргументы для callback
    """
    try:
        job_id = f"reminder_{user_id}_{reminder_time.timestamp()}"
        
        scheduler.add_job(
            callback,
            trigger=DateTrigger(run_date=reminder_time),
            id=job_id,
            args=[*args, user_id],
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"Добавлено одноразовое напоминание для пользователя {user_id} на {reminder_time}")
    except Exception as e:
        logger.error(f"Ошибка при добавлении одноразового напоминания: {e}")


async def remove_reminder(job_id: str):
    """
    Удаление напоминания
    
    Args:
        job_id: ID задачи
    """
    try:
        scheduler.remove_job(job_id)
        logger.info(f"Удалено напоминание {job_id}")
    except Exception as e:
        logger.error(f"Ошибка при удалении напоминания: {e}")


async def get_user_reminders(user_id: int) -> list:
    """
    Получение всех напоминаний пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        list: Список напоминаний
    """
    reminders = []
    for job in scheduler.get_jobs():
        if f"_{user_id}_" in job.id:
            reminders.append({
                "id": job.id,
                "next_run": job.next_run_time,
                "trigger": str(job.trigger)
            })
    return reminders

