from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    app_name: str = "Генератор учебных материалов"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # CORS настройки
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    # Настройки файлов
    
    # Настройки файлов
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    temp_dir: str = "./temp"
    generated_files_dir: str = "./generated_files"
    
    # Безопасность и лимиты
    rate_limit_per_minute: int = 60  # Лимит запросов в минуту для обычных эндпоинтов
    
    # Математический генератор
    max_operands: int = 10
    max_examples: int = 1000
    min_interval: int = -1000
    max_interval: int = 1000
    
    # КТП генератор
    max_lessons_per_day: int = 15
    
    # Дополнительные настройки
    




    model_config = {
        "case_sensitive": False,
        "extra": "ignore"
    }

# Создаем экземпляр настроек
settings = Settings()

# Создаем необходимые директории
os.makedirs(settings.temp_dir, exist_ok=True) 
os.makedirs(settings.generated_files_dir, exist_ok=True) 