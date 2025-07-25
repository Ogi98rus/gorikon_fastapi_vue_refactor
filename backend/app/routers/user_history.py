from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import Optional
import os
import hashlib
from datetime import datetime, timedelta

from app.models.database import get_db, Generation, User
from app.models.schemas import (
    GenerationListResponse, GenerationDetailResponse, 
    GenerationInfo, ResponseBase, UserProfileResponse
)
from app.dependencies.auth import get_current_user, get_current_active_user

router = APIRouter(prefix="/user", tags=["user-history"])

@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить расширенную информацию о профиле пользователя"""
    
    # Статистика генераций
    total_generations = db.query(Generation).filter(Generation.user_id == current_user.id).count()
    math_generations = db.query(Generation).filter(
        and_(Generation.user_id == current_user.id, Generation.generator_type == "math")
    ).count()
    ktp_generations = db.query(Generation).filter(
        and_(Generation.user_id == current_user.id, Generation.generator_type == "ktp")
    ).count()
    
    # Общее количество скачиваний
    total_downloads = db.query(func.sum(Generation.download_count)).filter(
        Generation.user_id == current_user.id
    ).scalar() or 0
    
    # Возраст аккаунта
    account_age = datetime.utcnow() - current_user.created_at
    account_age_days = account_age.days
    
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "school_name": current_user.school_name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat()
    }
    
    return UserProfileResponse(
        user=user_data,
        total_generations=total_generations,
        math_generations=math_generations,
        ktp_generations=ktp_generations,
        total_downloads=total_downloads,
        account_age_days=account_age_days,
        last_login=current_user.last_login
    )

@router.get("/generations", response_model=GenerationListResponse)
async def get_user_generations(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    generator_type: Optional[str] = Query(None, description="Тип генератора: math или ktp"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить список генераций пользователя с пагинацией"""
    
    # Базовый запрос
    query = db.query(Generation).filter(Generation.user_id == current_user.id)
    
    # Фильтр по типу генератора
    if generator_type:
        query = query.filter(Generation.generator_type == generator_type)
    
    # Общее количество
    total_count = query.count()
    
    # Применяем пагинацию и сортировку
    generations = query.order_by(desc(Generation.created_at))\
                      .offset((page - 1) * per_page)\
                      .limit(per_page)\
                      .all()
    
    # Преобразуем в схему ответа
    generation_list = []
    for gen in generations:
        generation_list.append(GenerationInfo(
            id=gen.id,
            generator_type=gen.generator_type,
            original_file_name=gen.original_file_name,
            file_size=gen.file_size,
            examples_generated=gen.examples_generated,
            total_lessons=gen.total_lessons,
            created_at=gen.created_at,
            download_count=gen.download_count,
            is_available=gen.is_available,
            expires_at=gen.expires_at,
            parameters=gen.parameters
        ))
    
    return GenerationListResponse(
        generations=generation_list,
        total_count=total_count,
        page=page,
        per_page=per_page
    )

@router.get("/generations/{generation_id}", response_model=GenerationDetailResponse)
async def get_generation_detail(
    generation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить детальную информацию о конкретной генерации"""
    
    generation = db.query(Generation).filter(
        and_(Generation.id == generation_id, Generation.user_id == current_user.id)
    ).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Генерация не найдена")
    
    generation_info = GenerationInfo(
        id=generation.id,
        generator_type=generation.generator_type,
        original_file_name=generation.original_file_name,
        file_size=generation.file_size,
        examples_generated=generation.examples_generated,
        total_lessons=generation.total_lessons,
        created_at=generation.created_at,
        download_count=generation.download_count,
        is_available=generation.is_available,
        expires_at=generation.expires_at,
        parameters=generation.parameters
    )
    
    return GenerationDetailResponse(generation=generation_info)

@router.get("/generations/{generation_id}/download")
async def download_generation_file(
    generation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Скачать файл генерации"""
    
    generation = db.query(Generation).filter(
        and_(Generation.id == generation_id, Generation.user_id == current_user.id)
    ).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Генерация не найдена")
    
    if not generation.is_available:
        raise HTTPException(status_code=410, detail="Файл больше не доступен")
    
    # Проверяем, не истек ли срок хранения
    if generation.expires_at and generation.expires_at < datetime.utcnow():
        generation.is_available = False
        db.commit()
        raise HTTPException(status_code=410, detail="Срок хранения файла истек")
    
    # Проверяем существование файла
    if not os.path.exists(generation.file_path):
        generation.is_available = False
        db.commit()
        raise HTTPException(status_code=410, detail="Файл не найден на сервере")
    
    # Проверяем целостность файла (если есть хеш)
    if generation.file_hash:
        with open(generation.file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
            if file_hash != generation.file_hash:
                generation.is_available = False
                db.commit()
                raise HTTPException(status_code=410, detail="Файл поврежден")
    
    # Увеличиваем счетчик скачиваний
    generation.download_count += 1
    db.commit()
    
    return FileResponse(
        path=generation.file_path,
        filename=generation.original_file_name,
        media_type='application/octet-stream'
    )

@router.delete("/generations/{generation_id}", response_model=ResponseBase)
async def delete_generation(
    generation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить генерацию из истории (файл остается на сервере)"""
    
    generation = db.query(Generation).filter(
        and_(Generation.id == generation_id, Generation.user_id == current_user.id)
    ).first()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Генерация не найдена")
    
    db.delete(generation)
    db.commit()
    
    return ResponseBase(message="Генерация удалена из истории")

@router.get("/statistics", response_model=dict)
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить подробную статистику пользователя"""
    
    # Статистика по периодам
    now = datetime.utcnow()
    
    # За последний месяц
    month_ago = now - timedelta(days=30)
    month_generations = db.query(Generation).filter(
        and_(
            Generation.user_id == current_user.id,
            Generation.created_at >= month_ago
        )
    ).count()
    
    # За последнюю неделю
    week_ago = now - timedelta(days=7)
    week_generations = db.query(Generation).filter(
        and_(
            Generation.user_id == current_user.id,
            Generation.created_at >= week_ago
        )
    ).count()
    
    # Самые популярные файлы (по скачиваниям)
    popular_files = db.query(Generation).filter(
        Generation.user_id == current_user.id
    ).order_by(desc(Generation.download_count)).limit(5).all()
    
    popular_files_data = [
        {
            "id": gen.id,
            "file_name": gen.original_file_name,
            "generator_type": gen.generator_type,
            "download_count": gen.download_count,
            "created_at": gen.created_at.isoformat()
        }
        for gen in popular_files
    ]
    
    # Общий размер файлов
    total_size = db.query(func.sum(Generation.file_size)).filter(
        Generation.user_id == current_user.id
    ).scalar() or 0
    
    return {
        "success": True,
        "statistics": {
            "total_generations": db.query(Generation).filter(Generation.user_id == current_user.id).count(),
            "month_generations": month_generations,
            "week_generations": week_generations,
            "total_downloads": db.query(func.sum(Generation.download_count)).filter(
                Generation.user_id == current_user.id
            ).scalar() or 0,
            "total_file_size": total_size,
            "popular_files": popular_files_data,
            "account_created": current_user.created_at.isoformat(),
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None
        }
    } 