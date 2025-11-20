"""
Модуль для работы с базой данных
"""
import aiosqlite
import os
from pathlib import Path
import config
from bot.utils.logger import logger


async def init_databases():
    """
    Инициализация всех баз данных
    """
    # Создаем директорию для баз данных
    os.makedirs(config.DB_PATH, exist_ok=True)
    
    # Инициализация базы расписания
    async with aiosqlite.connect(config.SCHEDULE_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                subject TEXT NOT NULL,
                time TEXT NOT NULL,
                room TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    
    # Инициализация базы домашних заданий
    async with aiosqlite.connect(config.HOMEWORK_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS homework (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                task TEXT NOT NULL,
                deadline DATE,
                is_completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    
    # Инициализация базы заметок
    async with aiosqlite.connect(config.NOTES_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    
    # Инициализация базы настроек пользователей
    settings_db = f"{config.DB_PATH}/settings.db"
    async with aiosqlite.connect(settings_db) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'ru',
                theme TEXT DEFAULT 'light',
                reminder_time TEXT DEFAULT '08:00',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    
    # Инициализация базы достижений
    achievements_db = f"{config.DB_PATH}/achievements.db"
    async with aiosqlite.connect(achievements_db) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_data TEXT,
                unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
    
    logger.info("Базы данных инициализированы")

