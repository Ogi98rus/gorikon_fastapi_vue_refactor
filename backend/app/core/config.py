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
    
    # База данных MySQL (единственная поддерживаемая)
    mysql_host: str = "mysql"  # Имя сервиса в docker-compose
    mysql_port: int = 3306
    mysql_user: str = "generator_user"
    mysql_password: str = "generator_password"
    mysql_database: str = "generator_db"

    
    # JWT настройки (для аутентификации)
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
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
    enable_analytics: bool = True
    enable_user_registration: bool = True
    email_from: str = "noreply@generator.localhost"
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    


    @property
    def database_url(self) -> str:
        """Получить URL для подключения к MySQL"""
        # Приоритет: переменная окружения DATABASE_URL, затем сборка из параметров MySQL
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url
        
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"

    model_config = {
        "case_sensitive": False,
        "extra": "ignore"
    }

# Создаем экземпляр настроек
settings = Settings()

# Создаем необходимые директории
os.makedirs(settings.temp_dir, exist_ok=True) 
os.makedirs(settings.generated_files_dir, exist_ok=True) 