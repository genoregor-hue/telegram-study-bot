"""
Модуль для форматирования вывода
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any


def format_date(date: datetime, format_str: str = "%d.%m.%y") -> str:
    """
    Форматирование даты
    
    Args:
        date: Объект datetime
        format_str: Формат даты
        
    Returns:
        str: Отформатированная дата
    """
    return date.strftime(format_str)


def format_time(time: str) -> str:
    """
    Форматирование времени
    
    Args:
        time: Время в формате HH:MM
        
    Returns:
        str: Отформатированное время
    """
    return time


def format_schedule_day(schedule_items: List[Dict[str, Any]], day: str) -> str:
    """
    Форматирование расписания на день
    
    Args:
        schedule_items: Список предметов
        day: Название дня
        
    Returns:
        str: Отформатированное расписание
    """
    if not schedule_items:
        return f"📅 <b>{day}</b>\n\nНет занятий"
    
    text = f"📅 <b>{day}</b>\n\n"
    for item in sorted(schedule_items, key=lambda x: x.get('time', '')):
        subject = item.get('subject', '')
        time = item.get('time', '')
        room = item.get('room', '')
        
        text += f"🕐 <b>{time}</b> - {subject}"
        if room:
            text += f" (каб. {room})"
        text += "\n"
    
    return text


def format_homework_list(homework_items: List[Dict[str, Any]], title: str = "Домашние задания") -> str:
    """
    Форматирование списка домашних заданий
    
    Args:
        homework_items: Список ДЗ
        title: Заголовок
        
    Returns:
        str: Отформатированный список
    """
    if not homework_items:
        return f"📘 <b>{title}</b>\n\nНет заданий"
    
    text = f"📘 <b>{title}</b>\n\n"
    for idx, item in enumerate(homework_items, 1):
        subject = item.get('subject', '')
        task = item.get('task', '')
        deadline = item.get('deadline', '')
        is_completed = item.get('is_completed', False)
        status = "✅" if is_completed else "⏳"
        
        text += f"{status} <b>{idx}.</b> {subject}\n"
        text += f"   {task}\n"
        if deadline:
            deadline_date = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline
            text += f"   📅 До: {format_date(deadline_date)}\n"
        text += "\n"
    
    return text


def format_progress_bar(percentage: float, length: int = 10) -> str:
    """
    Форматирование прогресс-бара
    
    Args:
        percentage: Процент выполнения (0-100)
        length: Длина бара
        
    Returns:
        str: Emoji-бар
    """
    filled = int(percentage / 100 * length)
    empty = length - filled
    
    # Выбор emoji в зависимости от процента
    if percentage >= 80:
        filled_emoji = "🟩"
    elif percentage >= 50:
        filled_emoji = "🟨"
    else:
        filled_emoji = "🟥"
    
    return filled_emoji * filled + "⬜" * empty


def format_notes_list(notes: List[Dict[str, Any]]) -> str:
    """
    Форматирование списка заметок
    
    Args:
        notes: Список заметок
        
    Returns:
        str: Отформатированный список
    """
    if not notes:
        return "📝 <b>Заметки</b>\n\nНет заметок"
    
    text = "📝 <b>Заметки</b>\n\n"
    for idx, note in enumerate(notes, 1):
        title = note.get('title', 'Без названия')
        content = note.get('content', '')
        created = note.get('created_at', '')
        
        text += f"<b>{idx}.</b> {title}\n"
        if content:
            preview = content[:50] + "..." if len(content) > 50 else content
            text += f"   {preview}\n"
        if created:
            created_date = datetime.fromisoformat(created) if isinstance(created, str) else created
            text += f"   📅 {format_date(created_date)}\n"
        text += "\n"
    
    return text


def get_day_name(date: datetime) -> str:
    """
    Получение названия дня недели
    
    Args:
        date: Дата
        
    Returns:
        str: Название дня
    """
    days = {
        0: "Понедельник",
        1: "Вторник",
        2: "Среда",
        3: "Четверг",
        4: "Пятница",
        5: "Суббота",
        6: "Воскресенье"
    }
    return days[date.weekday()]


def get_week_dates() -> List[tuple[datetime, str]]:
    """
    Получение дат текущей недели
    
    Returns:
        List[tuple]: Список кортежей (дата, название дня)
    """
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    week_dates = []
    for i in range(7):
        date = start_of_week + timedelta(days=i)
        day_name = get_day_name(datetime.combine(date, datetime.min.time()))
        week_dates.append((datetime.combine(date, datetime.min.time()), day_name))
    
    return week_dates

