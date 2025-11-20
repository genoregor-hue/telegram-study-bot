"""
Модель для работы с достижениями
"""
import aiosqlite
import config
from typing import List, Dict, Any
from bot.utils.logger import logger

achievements_db = f"{config.DB_PATH}/achievements.db"


async def add_achievement(user_id: int, achievement_type: str, achievement_data: str = "") -> int:
    """
    Добавление достижения
    
    Args:
        user_id: ID пользователя
        achievement_type: Тип достижения
        achievement_data: Дополнительные данные
        
    Returns:
        int: ID достижения
    """
    try:
        async with aiosqlite.connect(achievements_db) as db:
            cursor = await db.execute("""
                INSERT INTO achievements (user_id, achievement_type, achievement_data)
                VALUES (?, ?, ?)
            """, (user_id, achievement_type, achievement_data))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Ошибка при добавлении достижения: {e}")
        raise


async def get_user_achievements(user_id: int) -> List[Dict[str, Any]]:
    """
    Получение всех достижений пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        List[Dict]: Список достижений
    """
    try:
        async with aiosqlite.connect(achievements_db) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM achievements
                WHERE user_id = ?
                ORDER BY unlocked_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении достижений: {e}")
        return []


async def has_achievement(user_id: int, achievement_type: str) -> bool:
    """
    Проверка наличия достижения
    
    Args:
        user_id: ID пользователя
        achievement_type: Тип достижения
        
    Returns:
        bool: True если достижение есть
    """
    try:
        async with aiosqlite.connect(achievements_db) as db:
            async with db.execute("""
                SELECT COUNT(*) FROM achievements
                WHERE user_id = ? AND achievement_type = ?
            """, (user_id, achievement_type)) as cursor:
                count = (await cursor.fetchone())[0]
                return count > 0
    except Exception as e:
        logger.error(f"Ошибка при проверке достижения: {e}")
        return False


async def check_achievements(user_id: int, bot):
    """
    Проверка и выдача достижений
    
    Args:
        user_id: ID пользователя
        bot: Экземпляр бота
    """
    try:
        from bot.database.homework_model import get_homework_statistics, get_all_homework
        
        # Проверка достижения "5 ДЗ подряд"
        homework = await get_all_homework(user_id)
        completed_count = 0
        max_streak = 0
        
        for item in sorted(homework, key=lambda x: x.get('created_at', ''), reverse=True):
            if item.get('is_completed', False):
                completed_count += 1
                max_streak = max(max_streak, completed_count)
            else:
                completed_count = 0
        
        if max_streak >= 5 and not await has_achievement(user_id, "homework_streak_5"):
            await add_achievement(user_id, "homework_streak_5", f"Выполнено {max_streak} ДЗ подряд")
            await bot.send_message(
                user_id,
                "🎉 <b>Достижение разблокировано!</b>\n\n"
                "🏆 Сделал 5 ДЗ подряд\n\n"
                "Отличная работа! Продолжайте в том же духе!",
                parse_mode="HTML"
            )
        
        # Проверка достижения "10 выполненных ДЗ"
        stats = await get_homework_statistics(user_id)
        if stats.get('completed', 0) >= 10 and not await has_achievement(user_id, "homework_10"):
            await add_achievement(user_id, "homework_10", f"Выполнено {stats.get('completed', 0)} ДЗ")
            await bot.send_message(
                user_id,
                "🎉 <b>Достижение разблокировано!</b>\n\n"
                "🏆 Выполнено 10 домашних заданий\n\n"
                "Вы на правильном пути!",
                parse_mode="HTML"
            )
        
        # Проверка достижения "50 выполненных ДЗ"
        if stats.get('completed', 0) >= 50 and not await has_achievement(user_id, "homework_50"):
            await add_achievement(user_id, "homework_50", f"Выполнено {stats.get('completed', 0)} ДЗ")
            await bot.send_message(
                user_id,
                "🎉 <b>Достижение разблокировано!</b>\n\n"
                "🏆 Выполнено 50 домашних заданий\n\n"
                "Невероятный результат!",
                parse_mode="HTML"
            )
        
    except Exception as e:
        logger.error(f"Ошибка при проверке достижений: {e}")

