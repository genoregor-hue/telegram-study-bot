# Работа с Supabase
from supabase import create_client, Client
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import config
from bot.utils.logger import logger


class SupabaseDB:
    def __init__(self):
        try:
            if not config.SUPABASE_URL or not config.SUPABASE_KEY:
                raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть установлены в .env")
            
            self.supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            logger.info("Подключение к Supabase установлено")
        except Exception as e:
            logger.error(f"Ошибка при подключении к Supabase: {e}")
            raise
    
    def add_homework(self, subject: str, hw: str, deadline: Optional[date] = None) -> Dict[str, Any]:
        try:
            data = {
                "subject": subject,
                "hw": hw,
                "deadline": deadline.isoformat() if deadline else None
            }
            
            result = self.supabase.table("homework").insert(data).execute()
            
            if result.data:
                logger.info(f"Домашнее задание добавлено: {subject}")
                return result.data[0]
            else:
                raise Exception("Не удалось добавить домашнее задание")
                
        except Exception as e:
            logger.error(f"Ошибка при добавлении домашнего задания: {e}")
            raise
    
    def get_homework(self, deadline: Optional[date] = None, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            query = self.supabase.table("homework").select("*")
            
            if deadline:
                query = query.eq("deadline", deadline.isoformat())
            
            if subject:
                query = query.eq("subject", subject)
            
            result = query.order("deadline", desc=False).execute()
            
            logger.info(f"Получено домашних заданий: {len(result.data)}")
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Ошибка при получении домашних заданий: {e}")
            return []
    
    def add_schedule(self, date: date, subject: str, time: str) -> Dict[str, Any]:
        try:
            data = {
                "date": date.isoformat(),
                "subject": subject,
                "time": time
            }
            
            result = self.supabase.table("schedule").insert(data).execute()
            
            if result.data:
                logger.info(f"Расписание добавлено: {subject} на {date}")
                return result.data[0]
            else:
                raise Exception("Не удалось добавить расписание")
                
        except Exception as e:
            logger.error(f"Ошибка при добавлении расписания: {e}")
            raise
    
    def get_schedule(self, date: Optional[date] = None) -> List[Dict[str, Any]]:
        try:
            query = self.supabase.table("schedule").select("*")
            
            if date:
                query = query.eq("date", date.isoformat())
            
            result = query.order("time", desc=False).execute()
            
            logger.info(f"Получено записей расписания: {len(result.data)}")
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Ошибка при получении расписания: {e}")
            return []
    
    def update_homework(self, homework_id: int, subject: Optional[str] = None, 
                       hw: Optional[str] = None, deadline: Optional[date] = None) -> bool:
        try:
            data = {}
            if subject is not None:
                data["subject"] = subject
            if hw is not None:
                data["hw"] = hw
            if deadline is not None:
                data["deadline"] = deadline.isoformat()
            
            if not data:
                return False
            
            result = self.supabase.table("homework").update(data).eq("id", homework_id).execute()
            
            if result.data:
                logger.info(f"Домашнее задание {homework_id} обновлено")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении домашнего задания: {e}")
            return False
    
    def delete_homework(self, homework_id: int) -> bool:
        try:
            result = self.supabase.table("homework").delete().eq("id", homework_id).execute()
            logger.info(f"Домашнее задание {homework_id} удалено")
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении домашнего задания: {e}")
            return False
    
    def update_schedule(self, schedule_id: int, subject: Optional[str] = None,
                       time: Optional[str] = None, date: Optional[date] = None) -> bool:
        try:
            data = {}
            if subject is not None:
                data["subject"] = subject
            if time is not None:
                data["time"] = time
            if date is not None:
                data["date"] = date.isoformat()
            
            if not data:
                return False
            
            result = self.supabase.table("schedule").update(data).eq("id", schedule_id).execute()
            
            if result.data:
                logger.info(f"Расписание {schedule_id} обновлено")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении расписания: {e}")
            return False
    
    def delete_schedule(self, schedule_id: int) -> bool:
        try:
            result = self.supabase.table("schedule").delete().eq("id", schedule_id).execute()
            logger.info(f"Расписание {schedule_id} удалено")
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении расписания: {e}")
            return False


# Глобальный экземпляр для использования в проекте
_db_instance: Optional[SupabaseDB] = None


def get_db() -> SupabaseDB:
    # Singleton для подключения к БД
    global _db_instance
    if _db_instance is None:
        _db_instance = SupabaseDB()
    return _db_instance


# Обёртки для удобства использования
async def add_homework(subject: str, text: str, deadline: Optional[date] = None) -> Dict[str, Any]:
    db = get_db()
    return db.add_homework(subject, text, deadline)


async def get_homework(deadline: Optional[date] = None, subject: Optional[str] = None) -> List[Dict[str, Any]]:
    db = get_db()
    return db.get_homework(deadline, subject)


async def add_schedule(date: date, subject: str, time: str) -> Dict[str, Any]:
    db = get_db()
    return db.add_schedule(date, subject, time)


async def get_schedule(date: Optional[date] = None) -> List[Dict[str, Any]]:
    db = get_db()
    return db.get_schedule(date)

