# Настройки бота
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота (получить у @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Supabase настройки
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Пути к базам данных (для локальных БД, если нужны)
DB_PATH = "data"
SCHEDULE_DB = f"{DB_PATH}/schedule.db"
HOMEWORK_DB = f"{DB_PATH}/homework.db"
NOTES_DB = f"{DB_PATH}/notes.db"

# Путь к логам
LOGS_PATH = f"{DB_PATH}/logs"

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Настройки напоминаний
DEFAULT_REMINDER_TIME = "08:00"  # Время по умолчанию для напоминаний

# Языки
LANGUAGES = {
    "ru": "Русский",
    "en": "English"
}

# Темы
THEMES = {
    "light": "Светлая",
    "dark": "Темная",
    "color": "Цветная"
}

