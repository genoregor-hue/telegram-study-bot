"""
Модуль для настройки логирования
"""
import logging
import os
from datetime import datetime
from pathlib import Path
import config

# Создаем директорию для логов, если её нет
os.makedirs(config.LOGS_PATH, exist_ok=True)

# Настройка логирования
log_file = os.path.join(
    config.LOGS_PATH,
    f"bot_{datetime.now().strftime('%Y%m%d')}.log"
)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

