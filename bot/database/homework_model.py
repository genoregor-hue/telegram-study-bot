"""
Модель для работы с домашними заданиями
"""
import aiosqlite
import config
from typing import List, Dict, Any, Optional
from datetime import datetime
from bot.utils.logger import logger


async def add_homework(user_id: int, subject: str, task: str, deadline: Optional[datetime] = None) -> int:
    """
    Добавление домашнего задания
    
    Args:
        user_id: ID пользователя
        subject: Предмет
        task: Задание
        deadline: Дедлайн
        
    Returns:
        int: ID добавленного ДЗ
    """
    try:
        deadline_str = deadline.isoformat() if deadline else None
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            cursor = await db.execute("""
                INSERT INTO homework (user_id, subject, task, deadline, is_completed)
                VALUES (?, ?, ?, ?, 0)
            """, (user_id, subject, task, deadline_str))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Ошибка при добавлении ДЗ: {e}")
        raise


async def get_homework_by_date(user_id: int, date: datetime) -> List[Dict[str, Any]]:
    """
    Получение ДЗ на конкретную дату
    
    Args:
        user_id: ID пользователя
        date: Дата
        
    Returns:
        List[Dict]: Список ДЗ
    """
    try:
        date_str = date.date().isoformat()
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM homework
                WHERE user_id = ? AND date(deadline) = ?
                ORDER BY deadline
            """, (user_id, date_str)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении ДЗ: {e}")
        return []


async def get_homework_by_subject(user_id: int, subject: str) -> List[Dict[str, Any]]:
    """
    Получение ДЗ по предмету
    
    Args:
        user_id: ID пользователя
        subject: Предмет
        
    Returns:
        List[Dict]: Список ДЗ
    """
    try:
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM homework
                WHERE user_id = ? AND subject = ? AND is_completed = 0
                ORDER BY deadline
            """, (user_id, subject)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении ДЗ: {e}")
        return []


async def get_all_homework(user_id: int, include_completed: bool = False) -> List[Dict[str, Any]]:
    """
    Получение всех ДЗ пользователя
    
    Args:
        user_id: ID пользователя
        include_completed: Включать ли выполненные
        
    Returns:
        List[Dict]: Список ДЗ
    """
    try:
        query = """
            SELECT * FROM homework
            WHERE user_id = ?
        """
        params = [user_id]
        
        if not include_completed:
            query += " AND is_completed = 0"
        
        query += " ORDER BY deadline"
        
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении ДЗ: {e}")
        return []


async def mark_homework_completed(user_id: int, homework_id: int) -> bool:
    """
    Отметка ДЗ как выполненного
    
    Args:
        user_id: ID пользователя
        homework_id: ID ДЗ
        
    Returns:
        bool: True если успешно
    """
    try:
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            cursor = await db.execute("""
                UPDATE homework
                SET is_completed = 1
                WHERE id = ? AND user_id = ?
            """, (homework_id, user_id))
            await db.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Ошибка при отметке ДЗ: {e}")
        return False


async def delete_homework(user_id: int, homework_id: int) -> bool:
    """
    Удаление ДЗ
    
    Args:
        user_id: ID пользователя
        homework_id: ID ДЗ
        
    Returns:
        bool: True если успешно удалено
    """
    try:
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            cursor = await db.execute("""
                DELETE FROM homework
                WHERE id = ? AND user_id = ?
            """, (homework_id, user_id))
            await db.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Ошибка при удалении ДЗ: {e}")
        return False


async def update_homework(user_id: int, homework_id: int, subject: str = None,
                          task: str = None, deadline: Optional[datetime] = None) -> bool:
    """
    Обновление ДЗ
    
    Args:
        user_id: ID пользователя
        homework_id: ID ДЗ
        subject: Новый предмет
        task: Новое задание
        deadline: Новый дедлайн
        
    Returns:
        bool: True если успешно обновлено
    """
    try:
        updates = []
        params = []
        
        if subject:
            updates.append("subject = ?")
            params.append(subject)
        if task:
            updates.append("task = ?")
            params.append(task)
        if deadline:
            updates.append("deadline = ?")
            params.append(deadline.isoformat())
        
        if not updates:
            return False
        
        params.extend([homework_id, user_id])
        
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            await db.execute(f"""
                UPDATE homework
                SET {', '.join(updates)}
                WHERE id = ? AND user_id = ?
            """, params)
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении ДЗ: {e}")
        return False


async def get_homework_statistics(user_id: int) -> Dict[str, Any]:
    """
    Получение статистики по ДЗ
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Dict: Статистика (total, completed, percentage)
    """
    try:
        async with aiosqlite.connect(config.HOMEWORK_DB) as db:
            # Всего ДЗ
            async with db.execute("""
                SELECT COUNT(*) as total FROM homework WHERE user_id = ?
            """, (user_id,)) as cursor:
                total = (await cursor.fetchone())[0]
            
            # Выполненных ДЗ
            async with db.execute("""
                SELECT COUNT(*) as completed FROM homework 
                WHERE user_id = ? AND is_completed = 1
            """, (user_id,)) as cursor:
                completed = (await cursor.fetchone())[0]
            
            percentage = (completed / total * 100) if total > 0 else 0
            
            return {
                "total": total,
                "completed": completed,
                "percentage": round(percentage, 1)
            }
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        return {"total": 0, "completed": 0, "percentage": 0}

