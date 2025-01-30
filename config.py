import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / 'models'

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Не задан токен бота в переменных окружения")

# Пути к файлам
MODEL_PATH = MODELS_DIR / 'model.pth'

# Проверяем существование файла
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Файл модели не найден по пути: {MODEL_PATH}")

# Настройки изображений
MIN_IMAGE_SIZE = 32
MAX_IMAGE_SIZE = 2048
TARGET_SIZE = 256

# Настройки логирования
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
