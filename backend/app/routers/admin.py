from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from typing import Optional
from datetime import datetime, timedelta

from app.models.database import get_db, User, Generation, UserRole, UserStatus
from app.models.schemas import (
    UserListResponse, UserResponse, UserAdminUpdate, UserBanRequest, 
    UserUnbanRequest, ResponseBase, UserRoleEnum, UserStatusEnum
)
from app.dependencies.auth import get_current_superuser
from app.services.auth_service import UserService

router = APIRouter(prefix="/api/admin", tags=["Администрирование"])

# ============= УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ =============

@router.get("/users", response_model=UserListResponse)
async def get_users_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество пользователей на странице"),
    role: Optional[UserRoleEnum] = Query(None, description="Фильтр по роли"),
    status: Optional[UserStatusEnum] = Query(None, description="Фильтр по статусу"),
    search: Optional[str] = Query(None, description="Поиск по email или имени"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Получить список всех пользователей (только для администраторов)"""
    
    # Базовый запрос
    query = db.query(User)
    
    # Применяем фильтры
    if role:
        query = query.filter(User.role == role.value)
    
    if status:
        query = query.filter(User.status == status.value)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
                User.school_name.ilike(search_pattern)
            )
        )
    
    # Подсчет общего количества
    total_count = query.count()
    
    # Пагинация
    offset = (page - 1) * per_page
    users = query.order_by(desc(User.created_at)).offset(offset).limit(per_page).all()
    
    # Преобразование в ответ
    user_responses = []
    for user in users:
        user_responses.append(UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            school_name=user.school_name,
            role=UserRoleEnum(user.role.value),
            status=UserStatusEnum(user.status.value),
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            last_login=user.last_login,
            banned_until=user.banned_until,
            ban_reason=user.ban_reason
        ))
    
    return UserListResponse(
        users=user_responses,
        total_count=total_count,
        page=page,
        per_page=per_page
    )

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int = Path(..., description="ID пользователя"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Получить информацию о пользователе по ID"""
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        school_name=user.school_name,
        role=UserRoleEnum(user.role.value),
        status=UserStatusEnum(user.status.value),
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        last_login=user.last_login,
        banned_until=user.banned_until,
        ban_reason=user.ban_reason
    )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int = Path(..., description="ID пользователя"),
    update_data: UserAdminUpdate = ...,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Обновить информацию о пользователе (только для администраторов)"""
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Защита от изменения себя
    if user.id == current_user.id and update_data.role == UserRoleEnum.BANNED:
        raise HTTPException(status_code=400, detail="Нельзя заблокировать самого себя")
    
    # Обновляем поля
    update_dict = update_data.dict(exclude_unset=True)
    
    for field, value in update_dict.items():
        if field == "role" and value:
            user.role = UserRole(value.value)
            # Синхронизируем старые поля
            user.is_superuser = (value == UserRoleEnum.ADMIN)
        elif field == "status" and value:
            user.status = UserStatus(value.value)
            # Синхронизируем старые поля
            user.is_active = (value in [UserStatusEnum.ACTIVE])
        else:
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        school_name=user.school_name,
        role=UserRoleEnum(user.role.value),
        status=UserStatusEnum(user.status.value),
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        last_login=user.last_login,
        banned_until=user.banned_until,
        ban_reason=user.ban_reason
    )

# ============= БЛОКИРОВКА И РАЗБЛОКИРОВКА =============

@router.post("/users/{user_id}/ban", response_model=ResponseBase)
async def ban_user(
    user_id: int = Path(..., description="ID пользователя"),
    ban_data: UserBanRequest = ...,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Заблокировать пользователя"""
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Защита от блокировки себя
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя заблокировать самого себя")
    
    # Устанавливаем блокировку
    user.status = UserStatus.BANNED
    user.role = UserRole.BANNED
    user.is_active = False
    user.ban_reason = ban_data.ban_reason
    
    if ban_data.permanent:
        user.banned_until = None  # Постоянная блокировка
    else:
        user.banned_until = datetime.utcnow() + timedelta(hours=ban_data.ban_duration_hours)
    
    db.commit()
    
    return ResponseBase(
        message=f"Пользователь {user.email} заблокирован. Причина: {ban_data.ban_reason}"
    )

@router.post("/users/{user_id}/unban", response_model=ResponseBase)
async def unban_user(
    user_id: int = Path(..., description="ID пользователя"),
    unban_data: UserUnbanRequest = ...,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Разблокировать пользователя"""
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Снимаем блокировку
    user.status = UserStatus.ACTIVE
    user.role = UserRole.USER
    user.is_active = True
    user.banned_until = None
    user.ban_reason = None
    
    db.commit()
    
    return ResponseBase(
        message=f"Пользователь {user.email} разблокирован. Причина: {unban_data.reason}"
    )

# ============= УПРАВЛЕНИЕ РОЛЯМИ =============

@router.post("/users/{user_id}/role/{role}", response_model=ResponseBase)
async def set_user_role(
    user_id: int = Path(..., description="ID пользователя"),
    role: UserRoleEnum = Path(..., description="Новая роль"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Назначить роль пользователю"""
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Защита от изменения своей роли
    if user.id == current_user.id and role != UserRoleEnum.ADMIN:
        raise HTTPException(status_code=400, detail="Нельзя изменить свою роль администратора")
    
    # Устанавливаем роль
    user.role = UserRole(role.value)
    
    # Синхронизируем старые поля
    user.is_superuser = (role == UserRoleEnum.ADMIN)
    
    if role == UserRoleEnum.BANNED:
        user.status = UserStatus.BANNED
        user.is_active = False
    elif user.status == UserStatus.BANNED:
        user.status = UserStatus.ACTIVE
        user.is_active = True
    
    db.commit()
    
    return ResponseBase(
        message=f"Пользователю {user.email} назначена роль: {role.value}"
    )

# ============= СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ =============

@router.get("/users/{user_id}/profile", response_model=dict)
async def get_user_profile_admin(
    user_id: int = Path(..., description="ID пользователя"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Получить расширенную информацию о профиле пользователя (для администраторов)"""
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Статистика генераций
    total_generations = db.query(Generation).filter(Generation.user_id == user.id).count()
    math_generations = db.query(Generation).filter(
        Generation.user_id == user.id, 
        Generation.generator_type == "math"
    ).count()
    ktp_generations = db.query(Generation).filter(
        Generation.user_id == user.id, 
        Generation.generator_type == "ktp"
    ).count()
    
    # Общее количество скачиваний
    total_downloads = db.query(func.sum(Generation.download_count)).filter(
        Generation.user_id == user.id
    ).scalar() or 0
    
    # Общий размер файлов
    total_file_size = db.query(func.sum(Generation.file_size)).filter(
        Generation.user_id == user.id
    ).scalar() or 0
    
    # Последние генерации
    recent_generations = db.query(Generation).filter(
        Generation.user_id == user.id
    ).order_by(desc(Generation.created_at)).limit(10).all()
    
    return {
        "user": UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            school_name=user.school_name,
            role=UserRoleEnum(user.role.value),
            status=UserStatusEnum(user.status.value),
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            last_login=user.last_login,
            banned_until=user.banned_until,
            ban_reason=user.ban_reason
        ),
        "statistics": {
            "total_generations": total_generations,
            "math_generations": math_generations,
            "ktp_generations": ktp_generations,
            "total_downloads": total_downloads,
            "total_file_size": total_file_size,
            "account_age_days": (datetime.utcnow() - user.created_at).days,
        },
        "recent_generations": [
            {
                "id": gen.id,
                "generator_type": gen.generator_type,
                "file_name": gen.original_file_name,
                "created_at": gen.created_at.isoformat(),
                "file_size": gen.file_size,
                "download_count": gen.download_count
            }
            for gen in recent_generations
        ]
    }

@router.get("/users/{user_id}/status", response_model=dict)
async def get_user_status(
    user_id: int = Path(..., description="ID пользователя"),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Получить текущий статус пользователя"""
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Проверяем активность блокировки
    is_banned_active = False
    if user.banned_until:
        is_banned_active = datetime.utcnow() < user.banned_until
    elif user.status == UserStatus.BANNED:
        is_banned_active = True  # Постоянная блокировка
    
    return {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
        "status": user.status.value,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_banned": is_banned_active,
        "banned_until": user.banned_until.isoformat() if user.banned_until else None,
        "ban_reason": user.ban_reason,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat()
    }

# ============= СТАТИСТИКА СИСТЕМЫ =============

@router.get("/stats", response_model=dict)
async def get_system_stats(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """Получить общую статистику системы"""
    
    # Статистика пользователей
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    banned_users = db.query(User).filter(User.status == UserStatus.BANNED).count()
    admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    # Статистика генераций
    total_generations = db.query(Generation).count()
    math_generations = db.query(Generation).filter(Generation.generator_type == "math").count()
    ktp_generations = db.query(Generation).filter(Generation.generator_type == "ktp").count()
    
    # Статистика за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_users = db.query(User).filter(User.created_at >= thirty_days_ago).count()
    recent_generations = db.query(Generation).filter(Generation.created_at >= thirty_days_ago).count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "banned": banned_users,
            "admins": admin_users,
            "recent_registrations": recent_users
        },
        "generations": {
            "total": total_generations,
            "math": math_generations,
            "ktp": ktp_generations,
            "recent": recent_generations
        },
        "system": {
            "uptime_days": (datetime.utcnow() - datetime(2025, 1, 1)).days,  # Примерная дата запуска
            "database_type": "MySQL"
        }
    } 