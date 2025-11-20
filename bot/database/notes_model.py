"""
Модель для работы с заметками
"""
import aiosqlite
import config
from typing import List, Dict, Any, Optional
from bot.utils.logger import logger


async def add_note(user_id: int, title: str, content: str = "") -> int:
    """
    Добавление заметки
    
    Args:
        user_id: ID пользователя
        title: Заголовок заметки
        content: Содержание заметки
        
    Returns:
        int: ID добавленной заметки
    """
    try:
        async with aiosqlite.connect(config.NOTES_DB) as db:
            cursor = await db.execute("""
                INSERT INTO notes (user_id, title, content)
                VALUES (?, ?, ?)
            """, (user_id, title, content))
            await db.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Ошибка при добавлении заметки: {e}")
        raise


async def get_note(user_id: int, note_id: int) -> Optional[Dict[str, Any]]:
    """
    Получение заметки по ID
    
    Args:
        user_id: ID пользователя
        note_id: ID заметки
        
    Returns:
        Dict: Заметка или None
    """
    try:
        async with aiosqlite.connect(config.NOTES_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM notes
                WHERE id = ? AND user_id = ?
            """, (note_id, user_id)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        logger.error(f"Ошибка при получении заметки: {e}")
        return None


async def get_all_notes(user_id: int) -> List[Dict[str, Any]]:
    """
    Получение всех заметок пользователя
    
    Args:
        user_id: ID пользователя
        
    Returns:
        List[Dict]: Список заметок
    """
    try:
        async with aiosqlite.connect(config.NOTES_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM notes
                WHERE user_id = ?
                ORDER BY updated_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при получении заметок: {e}")
        return []


async def search_notes(user_id: int, query: str) -> List[Dict[str, Any]]:
    """
    Поиск заметок по запросу
    
    Args:
        user_id: ID пользователя
        query: Поисковый запрос
        
    Returns:
        List[Dict]: Список найденных заметок
    """
    try:
        search_pattern = f"%{query}%"
        async with aiosqlite.connect(config.NOTES_DB) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM notes
                WHERE user_id = ? AND (title LIKE ? OR content LIKE ?)
                ORDER BY updated_at DESC
            """, (user_id, search_pattern, search_pattern)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Ошибка при поиске заметок: {e}")
        return []


async def update_note(user_id: int, note_id: int, title: str = None, content: str = None) -> bool:
    """
    Обновление заметки
    
    Args:
        user_id: ID пользователя
        note_id: ID заметки
        title: Новый заголовок
        content: Новое содержание
        
    Returns:
        bool: True если успешно обновлено
    """
    try:
        updates = []
        params = []
        
        if title:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.extend([note_id, user_id])
        
        async with aiosqlite.connect(config.NOTES_DB) as db:
            await db.execute(f"""
                UPDATE notes
                SET {', '.join(updates)}
                WHERE id = ? AND user_id = ?
            """, params)
            await db.commit()
            return True
    except Exception as e:
        logger.error(f"Ошибка при обновлении заметки: {e}")
        return False


async def delete_note(user_id: int, note_id: int) -> bool:
    """
    Удаление заметки
    
    Args:
        user_id: ID пользователя
        note_id: ID заметки
        
    Returns:
        bool: True если успешно удалено
    """
    try:
        async with aiosqlite.connect(config.NOTES_DB) as db:
            cursor = await db.execute("""
                DELETE FROM notes
                WHERE id = ? AND user_id = ?
            """, (note_id, user_id))
            await db.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Ошибка при удалении заметки: {e}")
        return False

