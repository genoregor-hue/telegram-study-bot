"""
Модель для работы с расписанием
"""
import aiosqlite
import config
from typing import List, Dict, Any, Optional
from bot.utils.logger import logger


async def add_schedule_item(user_id: int, day_of_week: int, subject: str, time: str, room: str = "") -> int:
    """
    Добавление предмета в расписание
    
    Args:
        user_id: ID пользователя
        day_of_week: День недели (0-6)
        subject: Название предмета
        time: Время в формате HH:MM
        room: Номер кабинета
        
    Returns:
        int: ID добавленного элемента
    """
    try:
        async with aiosqlite.connect(config.SCHEDULE_DB) as db:
            cursor = await db.execute("""
                INSERT INTO schedule (user_id, day_of_week, subject, time, room)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, day_of_week, subject, time, room))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Ошибка при добавлении предмета: {e}")
        raise


async def get_schedule_by_day(user_id: int, day_of_week: int) -> List[Dict[str, Any]]:
    """
    Получение расписания на день
    
    Args:
        user_id: ID пользователя
        day_of_week: День недели (0-6)
        
    Returns:
        List[Dict]: Список предметов
    """
    try:
        async with aiosqlite.connect(config.SCHEDULE_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM schedule
                WHERE user_id = ? AND day_of_week = ?
                ORDER BY time
            """, (user_id, day_of_week)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении расписания: {e}")
        return []


async def get_all_schedule(user_id: int) -> List[Dict[str, Any]]:
    """
    Получение всего расписания пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        List[Dict]: Список всех предметов
    """
    try:
        async with aiosqlite.connect(config.SCHEDULE_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM schedule
                WHERE user_id = ?
                ORDER BY day_of_week, time
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении расписания: {e}")
        return []


async def delete_schedule_item(user_id: int, item_id: int) -> bool:
    """
    Удаление предмета из расписания
    
    Args:
        user_id: ID пользователя
        item_id: ID предмета
        
    Returns:
        bool: True если успешно удалено
    """
    try:
        async with aiosqlite.connect(config.SCHEDULE_DB) as db:
            cursor = await db.execute("""
                DELETE FROM schedule
                WHERE id = ? AND user_id = ?
            """, (item_id, user_id))
            await db.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Ошибка при удалении предмета: {e}")
        return False


async def update_schedule_item(user_id: int, item_id: int, subject: str = None, 
                               time: str = None, room: str = None) -> bool:
    """
    Обновление предмета в расписании
    
    Args:
        user_id: ID пользователя
        item_id: ID предмета
        subject: Новое название предмета
        time: Новое время
        room: Новый кабинет
        
    Returns:
        bool: True если успешно обновлено
    """
    try:
        updates = []
        params = []
        
        if subject:
            updates.append("subject = ?")
            params.append(subject)
        if time:
            updates.append("time = ?")
            params.append(time)
        if room is not None:
            updates.append("room = ?")
            params.append(room)
        
        if not updates:
            return False
        
        params.extend([item_id, user_id])
        
        async with aiosqlite.connect(config.SCHEDULE_DB) as db:
            await db.execute(f"""
                UPDATE schedule
                SET {', '.join(updates)}
                WHERE id = ? AND user_id = ?
            """, params)
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении предмета: {e}")
        return False

