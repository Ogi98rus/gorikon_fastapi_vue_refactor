from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from app.core.config import settings

# Создание движка базы данных MySQL
engine = create_engine(
    settings.database_url,
    pool_recycle=3600,      # Переподключение к MySQL каждый час
    pool_pre_ping=True,     # Проверка соединения перед использованием
    pool_size=10,           # Размер пула соединений
    max_overflow=20,        # Максимальное количество дополнительных соединений
    echo=settings.debug     # Логирование SQL запросов в debug режиме
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ============= ENUM-Ы =============

class UserRole(enum.Enum):
    """Роли пользователей"""
    USER = "user"        # Обычный пользователь
    ADMIN = "admin"      # Администратор
    MODERATOR = "moderator"  # Модератор
    BANNED = "banned"    # Заблокированный пользователь

class UserStatus(enum.Enum):
    """Статусы пользователей"""
    ACTIVE = "active"         # Активен
    INACTIVE = "inactive"     # Неактивен
    SUSPENDED = "suspended"   # Приостановлен
    BANNED = "banned"         # Заблокирован

# ============= МОДЕЛИ ПОЛЬЗОВАТЕЛЕЙ =============

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    school_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Система ролей и статусов
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Старые поля для совместимости
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Мета-данные
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    banned_until = Column(DateTime, nullable=True)  # Дата окончания блокировки
    ban_reason = Column(Text, nullable=True)         # Причина блокировки
    
    # Связи
    generations = relationship("Generation", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

# ============= МОДЕЛИ АНАЛИТИКИ =============

class Generation(Base):
    """Модель записи о генерации файла"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Может быть анонимным
    generator_type = Column(String(50), nullable=False)  # "math" или "ktp"
    
    # Параметры генерации
    parameters = Column(JSON, nullable=False)
    
    # Информация о файле
    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)  # Имя, которое видит пользователь
    file_path = Column(String(500), nullable=False)  # Полный путь к файлу на сервере
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=True)  # SHA-256 хеш файла для проверки целостности
    
    # Результаты генерации
    examples_generated = Column(Integer, nullable=True)  # Для математических примеров
    total_lessons = Column(Integer, nullable=True)  # Для КТП
    
    # Статус файла
    is_available = Column(Boolean, default=True)  # Доступен ли файл для скачивания
    download_count = Column(Integer, default=0)  # Количество скачиваний
    expires_at = Column(DateTime, nullable=True)  # Дата истечения срока хранения файла
    
    # Мета-информация
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Integer, nullable=True)  # Время генерации в миллисекундах
    
    # Связи
    user = relationship("User", back_populates="generations")

class UserSession(Base):
    """Модель пользовательской сессии"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Связи
    user = relationship("User", back_populates="sessions")

# ============= СОЗДАНИЕ ТАБЛИЦ =============

def create_tables():
    """Создание всех таблиц в базе данных"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 