from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from collections import Counter
import time

from app.models.database import Generation, User
from app.models.schemas import GenerationStats, AnalyticsResponse

class AnalyticsService:
    """Сервис для сбора и анализа статистики"""
    
    @staticmethod
    def log_generation(
        db: Session,
        user_id: Optional[int],
        generator_type: str,
        parameters: Dict[str, Any],
        file_name: str,
        file_size: int,
        original_file_name: Optional[str] = None,
        file_path: Optional[str] = None,
        file_hash: Optional[str] = None,
        examples_generated: Optional[int] = None,
        total_lessons: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        processing_time: Optional[int] = None
    ) -> Generation:
        """Логирование генерации файла"""
        
        generation = Generation(
            user_id=user_id,
            generator_type=generator_type,
            parameters=parameters,
            file_name=file_name,
            original_file_name=original_file_name or file_name,  # Fallback к file_name если не передан
            file_path=file_path or "",  # Пустая строка если не передан
            file_size=file_size,
            file_hash=file_hash,
            examples_generated=examples_generated,
            total_lessons=total_lessons,
            ip_address=ip_address,
            user_agent=user_agent,
            processing_time=processing_time
        )
        
        db.add(generation)
        db.commit()
        db.refresh(generation)
        
        return generation
    
    @staticmethod
    def get_generation_stats(
        db: Session, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None,
        user_id: Optional[int] = None
    ) -> GenerationStats:
        """Получение статистики генераций"""
        
        # Устанавливаем период по умолчанию (последние 30 дней)
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Базовый запрос
        base_query = db.query(Generation).filter(
            and_(
                Generation.created_at >= start_date,
                Generation.created_at <= end_date
            )
        )
        
        # Фильтр по пользователю если указан
        if user_id:
            base_query = base_query.filter(Generation.user_id == user_id)
        
        # Общее количество генераций
        total_generations = base_query.count()
        
        # Количество по типам
        math_generations = base_query.filter(Generation.generator_type == "math").count()
        ktp_generations = base_query.filter(Generation.generator_type == "ktp").count()
        
        # Общий размер файлов
        total_files_size = db.query(func.sum(Generation.file_size)).filter(
            and_(
                Generation.created_at >= start_date,
                Generation.created_at <= end_date,
                Generation.user_id == user_id if user_id else True
            )
        ).scalar() or 0
        
        # Среднее количество примеров
        avg_examples = db.query(func.avg(Generation.examples_generated)).filter(
            and_(
                Generation.created_at >= start_date,
                Generation.created_at <= end_date,
                Generation.generator_type == "math",
                Generation.examples_generated.isnot(None),
                Generation.user_id == user_id if user_id else True
            )
        ).scalar() or 0
        
        # Самые популярные операции (для математических примеров)
        math_generations_data = base_query.filter(
            Generation.generator_type == "math"
        ).all()
        
        operations_counter = Counter()
        for gen in math_generations_data:
            if gen.parameters and "operations" in gen.parameters:
                operations = gen.parameters["operations"]
                if isinstance(operations, list):
                    operations_counter.update(operations)
        
        most_popular_operations = [op for op, count in operations_counter.most_common(4)]
        
        # Генерации по датам (последние 7 дней)
        generations_by_date = {}
        for i in range(7):
            day = end_date - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count = base_query.filter(
                and_(
                    Generation.created_at >= day_start,
                    Generation.created_at < day_end
                )
            ).count()
            
            generations_by_date[day.strftime("%Y-%m-%d")] = count
        
        return GenerationStats(
            total_generations=total_generations,
            math_generations=math_generations,
            ktp_generations=ktp_generations,
            total_files_size=total_files_size,
            average_examples_per_generation=round(avg_examples, 2),
            most_popular_operations=most_popular_operations,
            generations_by_date=generations_by_date
        )
    
    @staticmethod
    def get_user_generations(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Generation]:
        """Получение списка генераций пользователя"""
        
        return db.query(Generation).filter(
            Generation.user_id == user_id
        ).order_by(
            desc(Generation.created_at)
        ).offset(offset).limit(limit).all()
    
    @staticmethod
    def get_recent_generations(
        db: Session,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получение последних генераций (анонимизированно)"""
        
        recent = db.query(Generation).order_by(
            desc(Generation.created_at)
        ).limit(limit).all()
        
        result = []
        for gen in recent:
            result.append({
                "id": gen.id,
                "generator_type": gen.generator_type,
                "created_at": gen.created_at.isoformat(),
                "file_size": gen.file_size,
                "examples_generated": gen.examples_generated,
                "total_lessons": gen.total_lessons,
                "has_user": gen.user_id is not None
            })
        
        return result
    
    @staticmethod
    def get_system_stats(db: Session) -> Dict[str, Any]:
        """Получение общей системной статистики"""
        
        # Общие счетчики
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        total_generations = db.query(Generation).count()
        
        # Статистика за последние 24 часа
        last_24h = datetime.utcnow() - timedelta(hours=24)
        recent_generations = db.query(Generation).filter(
            Generation.created_at >= last_24h
        ).count()
        
        # Статистика за последнюю неделю
        last_week = datetime.utcnow() - timedelta(days=7)
        week_generations = db.query(Generation).filter(
            Generation.created_at >= last_week
        ).count()
        
        # Средний размер файла
        avg_file_size = db.query(func.avg(Generation.file_size)).scalar() or 0
        
        # Среднее время обработки
        avg_processing_time = db.query(func.avg(Generation.processing_time)).filter(
            Generation.processing_time.isnot(None)
        ).scalar() or 0
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_generations": total_generations,
            "recent_generations_24h": recent_generations,
            "recent_generations_week": week_generations,
            "average_file_size_bytes": round(avg_file_size, 2),
            "average_processing_time_ms": round(avg_processing_time, 2)
        }
    
    @staticmethod
    def cleanup_old_generations(db: Session, days_to_keep: int = 90) -> int:
        """Очистка старых записей о генерациях"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = db.query(Generation).filter(
            Generation.created_at < cutoff_date
        ).delete()
        
        db.commit()
        
        return deleted_count

# Вспомогательные функции
def measure_processing_time(func):
    """Декоратор для измерения времени выполнения функции"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        processing_time = int((end_time - start_time) * 1000)  # в миллисекундах
        return result, processing_time
    return wrapper 