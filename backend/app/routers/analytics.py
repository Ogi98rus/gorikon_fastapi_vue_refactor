from fastapi import APIRouter, Depends, HTTPException, Query, Request, Form
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Optional, List
from pydantic import BaseModel

from app.models.database import get_db, User
from app.models.schemas import AnalyticsResponse, GenerationStats
from app.services.analytics_service import AnalyticsService
from app.dependencies.auth import get_current_user, get_current_active_user, get_current_superuser, get_client_ip

router = APIRouter(prefix="/api/analytics", tags=["Аналитика"])

@router.get("/user/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики пользователя
    """
    try:
        # Получаем статистику пользователя за последние 30 дней
        user_stats = AnalyticsService.get_generation_stats(
            db,
            user_id=current_user.id,
            start_date=datetime.utcnow() - timedelta(days=30)
        )
        
        return {
            "success": True,
            "stats": {
                "total_generations": user_stats.total_generations,
                "math_generations": user_stats.math_generations,
                "ktp_generations": user_stats.ktp_generations,
                "total_files_size": user_stats.total_files_size,
                "average_examples": user_stats.average_examples_per_generation,
                "generations_by_date": user_stats.generations_by_date
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "stats": {
                "total_generations": 0,
                "math_generations": 0,
                "ktp_generations": 0,
                "total_files_size": 0,
                "average_examples": 0,
                "generations_by_date": {}
            }
        }

@router.get("/user/activity")
async def get_user_activity(
    limit: int = Query(5, ge=1, le=50, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение последней активности пользователя
    """
    try:
        # Получаем последние генерации пользователя
        user_generations = AnalyticsService.get_user_generations(
            db, 
            current_user.id, 
            limit=limit,
            offset=offset
        )
        
        activities = []
        for gen in user_generations:
            activities.append({
                "id": gen.id,
                "type": gen.generator_type,
                "file_name": gen.file_name,
                "created_at": gen.created_at.isoformat(),
                "file_size": gen.file_size,
                "examples_generated": gen.examples_generated,
                "total_lessons": gen.total_lessons
            })
        
        return {
            "success": True,
            "activities": activities,
            "total": len(activities),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        return {
            "success": False,
            "activities": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }

@router.get("/dashboard")
async def get_dashboard_data(
    date_range: str = Query("week", pattern="^(day|week|month|year)$", description="Период"),
    generation_type: str = Query("all", pattern="^(all|math|ktp)$", description="Тип генерации"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение данных для дашборда аналитики
    """
    try:
        # Определяем период
        now = datetime.utcnow()
        if date_range == "day":
            start_date = now - timedelta(days=1)
        elif date_range == "week":
            start_date = now - timedelta(weeks=1)
        elif date_range == "month":
            start_date = now - timedelta(days=30)
        else:  # year
            start_date = now - timedelta(days=365)
        
        # Получаем статистику
        if current_user:
            stats = AnalyticsService.get_generation_stats(
                db,
                user_id=current_user.id,
                start_date=start_date,
                generator_type=generation_type if generation_type != "all" else None
            )
        else:
            # Общая статистика для анонимных пользователей
            stats = AnalyticsService.get_generation_stats(
                db,
                start_date=start_date,
                generator_type=generation_type if generation_type != "all" else None
            )
        
        return {
            "success": True,
            "period": date_range,
            "generation_type": generation_type,
            "stats": {
                "total_generations": stats.total_generations,
                "math_generations": stats.math_generations,
                "ktp_generations": stats.ktp_generations,
                "total_files_size": stats.total_files_size,
                "average_examples": stats.average_examples_per_generation,
                "generations_by_date": stats.generations_by_date
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "period": date_range,
            "generation_type": generation_type,
            "stats": {
                "total_generations": 0,
                "math_generations": 0,
                "ktp_generations": 0,
                "total_files_size": 0,
                "average_examples": 0,
                "generations_by_date": {}
            }
        }

@router.get("/stats", response_model=AnalyticsResponse)
async def get_generation_stats(
    start_date: Optional[date] = Query(None, description="Дата начала периода"),
    end_date: Optional[date] = Query(None, description="Дата окончания периода"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Получение детальной статистики генераций для аутентифицированного пользователя
    """
    try:
        # Преобразуем даты в datetime
        start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
        end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
        
        stats = AnalyticsService.get_generation_stats(
            db,
            start_date=start_datetime,
            end_date=end_datetime,
            user_id=current_user.id
        )
        
        return AnalyticsResponse(
            stats=stats,
            period_start=start_date or (datetime.utcnow() - timedelta(days=30)).date(),
            period_end=end_date or datetime.utcnow().date()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

@router.get("/my-generations")
async def get_user_generations(
    limit: int = Query(50, ge=1, le=100, description="Количество записей"),
    offset: int = Query(0, ge=0, description="Смещение"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получение истории генераций пользователя"""
    try:
        generations = AnalyticsService.get_user_generations(
            db, 
            current_user.id, 
            limit=limit, 
            offset=offset
        )
        
        result = []
        for gen in generations:
            result.append({
                "id": gen.id,
                "generator_type": gen.generator_type,
                "file_name": gen.file_name,
                "file_size": gen.file_size,
                "examples_generated": gen.examples_generated,
                "total_lessons": gen.total_lessons,
                "created_at": gen.created_at.isoformat(),
                "processing_time": gen.processing_time,
                "parameters": gen.parameters
            })
        
        return {
            "generations": result,
            "total_count": len(result),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")

@router.get("/system-stats")
async def get_system_stats(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Получение системной статистики (только для суперпользователей)"""
    try:
        stats = AnalyticsService.get_system_stats(db)
        
        # Дополнительная детальная статистика
        recent_activity = AnalyticsService.get_recent_generations(db, limit=20)
        
        return {
            "system_stats": stats,
            "recent_activity": recent_activity,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения системной статистики: {str(e)}")

@router.post("/cleanup")
async def cleanup_old_data(
    days_to_keep: int = Query(90, ge=30, le=365, description="Количество дней для хранения"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Очистка старых данных аналитики (только для суперпользователей)"""
    try:
        deleted_count = AnalyticsService.cleanup_old_generations(db, days_to_keep)
        
        return {
            "message": f"Очищено {deleted_count} старых записей",
            "days_kept": days_to_keep,
            "cleaned_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки данных: {str(e)}")

@router.get("/export")
async def export_user_data(
            format: str = Query("json", pattern="^(json|csv)$", description="Формат экспорта"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Экспорт данных пользователя"""
    try:
        generations = AnalyticsService.get_user_generations(
            db, 
            current_user.id, 
            limit=1000  # Экспортируем до 1000 последних записей
        )
        
        if format == "json":
            data = []
            for gen in generations:
                data.append({
                    "id": gen.id,
                    "generator_type": gen.generator_type,
                    "file_name": gen.file_name,
                    "file_size": gen.file_size,
                    "examples_generated": gen.examples_generated,
                    "total_lessons": gen.total_lessons,
                    "created_at": gen.created_at.isoformat(),
                    "processing_time": gen.processing_time,
                    "parameters": gen.parameters
                })
            
            return {
                "user_id": current_user.id,
                "user_email": current_user.email,
                "export_date": datetime.utcnow().isoformat(),
                "generations": data
            }
        
        # TODO: Реализовать CSV экспорт при необходимости
        elif format == "csv":
            raise HTTPException(status_code=501, detail="CSV экспорт будет реализован позже")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка экспорта данных: {str(e)}") 

from pydantic import BaseModel

class PageViewRequest(BaseModel):
    page: str
    path: Optional[str] = None
    from_page: Optional[str] = None
    timestamp: Optional[str] = None

@router.post("/track/page-view")
async def track_page_view(
    request: Request,
    page_view: PageViewRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Трекинг просмотра страницы для аналитики
    """
    try:
        # Получаем IP адрес
        client_ip = get_client_ip(request)
        
        # Простое логирование (без track_event которого нет)
        if current_user:
            # Логируем как обычную генерацию с типом "page_view"  
            user_agent = request.headers.get("User-Agent", "")
            AnalyticsService.log_generation(
                db=db,
                user_id=current_user.id,
                generator_type="page_view",
                parameters={
                    "page": page_view.page, 
                    "path": page_view.path,
                    "from_page": page_view.from_page,
                    "timestamp": page_view.timestamp
                },
                file_name="",
                file_size=0,
                ip_address=client_ip,
                user_agent=user_agent,
                processing_time=0
            )
        
        return {"success": True, "message": "Page view tracked"}
        
    except Exception as e:
        # Не критично если трекинг не сработал
        return {"success": False, "message": f"Tracking failed: {str(e)}"} 