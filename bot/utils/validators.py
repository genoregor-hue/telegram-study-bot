"""
Модуль для валидации пользовательского ввода
"""
from datetime import datetime
import re


def validate_time(time_str: str) -> tuple[bool, str]:
    """
    Валидация времени в формате HH:MM
    
    Args:
        time_str: Строка времени
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not time_str:
        return False, "Время не может быть пустым"
    
    # Проверка формата HH:MM
    pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$'
    if not re.match(pattern, time_str):
        return False, "Неверный формат времени. Используйте HH:MM (например, 09:30)"
    
    return True, ""


def validate_date(date_str: str) -> tuple[bool, str, datetime | None]:
    """
    Валидация даты в формате DD.MM.YY или DD.MM.YYYY
    
    Args:
        date_str: Строка даты
        
    Returns:
        tuple: (is_valid, error_message, datetime_object)
    """
    if not date_str:
        return False, "Дата не может быть пустой", None
    
    # Поддержка форматов DD.MM.YY и DD.MM.YYYY
    patterns = [
        r'^(\d{1,2})\.(\d{1,2})\.(\d{2})$',  # DD.MM.YY
        r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$'   # DD.MM.YYYY
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_str)
        if match:
            day, month, year = match.groups()
            day, month, year = int(day), int(month), int(year)
            
            # Преобразование двухзначного года
            if year < 100:
                year += 2000 if year < 50 else 1900
            
            try:
                date_obj = datetime(year, month, day)
                # Проверка, что дата не в прошлом (для дедлайнов)
                if date_obj.date() < datetime.now().date():
                    return False, "Дата не может быть в прошлом", None
                return True, "", date_obj
            except ValueError:
                return False, "Неверная дата. Проверьте день и месяц", None
    
    return False, "Неверный формат даты. Используйте DD.MM.YY или DD.MM.YYYY (например, 25.12.24)", None


def validate_text(text: str, min_length: int = 1, max_length: int = 500) -> tuple[bool, str]:
    """
    Валидация текста
    
    Args:
        text: Текст для проверки
        min_length: Минимальная длина
        max_length: Максимальная длина
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not text:
        return False, f"Текст не может быть пустым"
    
    if len(text) < min_length:
        return False, f"Текст должен содержать минимум {min_length} символов"
    
    if len(text) > max_length:
        return False, f"Текст не должен превышать {max_length} символов"
    
    return True, ""


def validate_room(room: str) -> tuple[bool, str]:
    """
    Валидация номера кабинета
    
    Args:
        room: Номер кабинета
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not room:
        return True, ""  # Кабинет не обязателен
    
    if len(room) > 20:
        return False, "Номер кабинета не должен превышать 20 символов"
    
    return True, ""

