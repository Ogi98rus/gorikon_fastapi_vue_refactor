import os
import hashlib
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.database import Generation, User
from app.core.config import settings


class GenerationService:
    """Сервис для работы с записями генераций"""
    
    @staticmethod
    def create_generation_record(
        db: Session,
        generator_type: str,
        parameters: Dict[str, Any],
        file_path: str,
        original_file_name: str,
        user: Optional[User] = None,
        examples_generated: Optional[int] = None,
        total_lessons: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        processing_time: Optional[int] = None
    ) -> Generation:
        """
        Создать запись о генерации в базе данных
        
        Args:
            db: Сессия базы данных
            generator_type: Тип генератора ('math' или 'ktp')
            parameters: Параметры генерации
            file_path: Полный путь к файлу
            original_file_name: Имя файла для пользователя
            user: Пользователь (если авторизован)
            examples_generated: Количество сгенерированных примеров
            total_lessons: Общее количество уроков
            ip_address: IP адрес пользователя
            user_agent: User-Agent браузера
            processing_time: Время генерации в миллисекундах
            
        Returns:
            Generation: Созданная запись генерации
        """
        
        # Получаем информацию о файле
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # Вычисляем хеш файла для проверки целостности
        file_hash = None
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
        except Exception:
            pass  # Если не удалось вычислить хеш, продолжаем без него
        
        # Устанавливаем срок хранения файла (30 дней для авторизованных, 7 дней для анонимных)
        expires_at = None
        if user:
            expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Создаем запись
        generation = Generation(
            user_id=user.id if user else None,
            generator_type=generator_type,
            parameters=parameters,
            file_name=file_name,
            original_file_name=original_file_name,
            file_path=file_path,
            file_size=file_size,
            file_hash=file_hash,
            examples_generated=examples_generated,
            total_lessons=total_lessons,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            processing_time=processing_time
        )
        
        db.add(generation)
        db.commit()
        db.refresh(generation)
        
        return generation
    
    @staticmethod
    def save_file_permanently(temp_file_path: str, generator_type: str, original_name: str) -> str:
        """
        Переместить файл из временной папки в постоянное хранилище
        
        Args:
            temp_file_path: Путь к временному файлу
            generator_type: Тип генератора
            original_name: Оригинальное имя файла
            
        Returns:
            str: Путь к сохраненному файлу
        """
        
        # Создаем структуру папок: generated_files/generator_type/YYYY/MM/DD/
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        
        target_dir = os.path.join(
            settings.generated_files_dir,
            generator_type,
            date_path
        )
        
        # Создаем папки если их нет
        os.makedirs(target_dir, exist_ok=True)
        
        # Генерируем уникальное имя файла с timestamp
        timestamp = now.strftime("%H%M%S")
        name, ext = os.path.splitext(original_name)
        unique_filename = f"{name}_{timestamp}_{hashlib.md5(str(now).encode()).hexdigest()[:8]}{ext}"
        
        target_path = os.path.join(target_dir, unique_filename)
        
        # Копируем файл
        shutil.copy2(temp_file_path, target_path)
        
        # Удаляем временный файл
        try:
            os.remove(temp_file_path)
        except Exception:
            pass  # Игнорируем ошибки удаления временного файла
        
        return target_path
    
    @staticmethod
    def get_user_generations(
        db: Session,
        user_id: int,
        generator_type: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[Generation]:
        """
        Получить генерации пользователя
        
        Args:
            db: Сессия базы данных
            user_id: ID пользователя
            generator_type: Тип генератора для фильтрации
            limit: Максимальное количество записей
            offset: Смещение для пагинации
            
        Returns:
            list[Generation]: Список генераций
        """
        
        query = db.query(Generation).filter(Generation.user_id == user_id)
        
        if generator_type:
            query = query.filter(Generation.generator_type == generator_type)
        
        return query.order_by(Generation.created_at.desc())\
                   .offset(offset)\
                   .limit(limit)\
                   .all()
    
    @staticmethod
    def cleanup_expired_files():
        """
        Очистка файлов с истекшим сроком хранения
        Этот метод можно вызывать по расписанию
        """
        
        # TODO: Реализовать очистку истекших файлов
        # Можно использовать с celery или другим планировщиком задач
        pass
    
    @staticmethod
    def get_generation_by_id(db: Session, generation_id: int, user_id: Optional[int] = None) -> Optional[Generation]:
        """
        Получить генерацию по ID
        
        Args:
            db: Сессия базы данных
            generation_id: ID генерации
            user_id: ID пользователя (для проверки прав доступа)
            
        Returns:
            Generation или None
        """
        
        query = db.query(Generation).filter(Generation.id == generation_id)
        
        if user_id is not None:
            query = query.filter(Generation.user_id == user_id)
        
        return query.first() 