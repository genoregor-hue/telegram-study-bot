# Запуск Telegram бота для учебы
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
from bot.database.supabase_db import get_db
from bot.utils.logger import logger
from bot.utils.reminder_scheduler import start_scheduler, stop_scheduler
from bot.handlers import (
    start, schedule, homework, notes, reminders, progress, settings, errors
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT
)


async def main():
    # Проверка токена
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Создайте файл .env и добавьте BOT_TOKEN=your_token")
        return
    
    # Проверка Supabase настроек
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        logger.error("SUPABASE_URL и SUPABASE_KEY должны быть установлены в .env")
        return
    
    # Инициализация подключения к Supabase
    logger.info("Подключение к Supabase...")
    try:
        db = get_db()
        logger.info("Подключение к Supabase успешно установлено")
    except Exception as e:
        logger.error(f"Ошибка при подключении к Supabase: {e}")
        return
    
    # Создание бота и диспетчера
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров
    dp.include_router(start.router)
    dp.include_router(schedule.router)
    dp.include_router(homework.router)
    dp.include_router(notes.router)
    dp.include_router(reminders.router)
    dp.include_router(progress.router)
    dp.include_router(settings.router)
    dp.include_router(errors.router)
    
    # Запуск планировщика напоминаний
    start_scheduler()
    
    logger.info("Бот запущен!")
    
    try:
        # Запуск бота
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Остановка планировщика
        stop_scheduler()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)

