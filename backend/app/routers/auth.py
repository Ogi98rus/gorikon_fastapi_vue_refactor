from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db, User
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse
from app.services.auth_service import UserService, create_token_response, user_to_response
from app.dependencies.auth import (
    get_current_user, get_current_active_user, 
    get_client_ip, get_user_agent
)

router = APIRouter(prefix="/api/auth", tags=["Аутентификация"])

@router.post("/register", response_model=Token)
async def register_user(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    school_name: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя
    
    **Параметры:**
    - `email`: Электронная почта (уникальная)
    - `full_name`: Полное имя пользователя
    - `password`: Пароль (минимум 8 символов)
    - `school_name`: Название школы (необязательно)
    """
    try:
        # Валидация данных
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль должен содержать минимум 8 символов"
            )
        
        if len(full_name.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя должно содержать минимум 2 символа"
            )
        
        # Создаем объект данных пользователя
        user_data = UserCreate(
            email=email,
            full_name=full_name.strip(),
            password=password,
            school_name=school_name.strip() if school_name else None
        )
        
        user = UserService.create_user(db, user_data)
        
        # Создаем сессию
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        session = UserService.create_user_session(db, user.id, ip_address, user_agent)
        
        # Возвращаем токен
        return create_token_response(user, session.session_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка регистрации: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Вход пользователя в систему
    
    **Параметры:**
    - `username`: Email пользователя
    - `password`: Пароль
    """
    try:
        # Аутентификация пользователя
        user = UserService.authenticate_user(db, form_data.username, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Создаем новую сессию
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        session = UserService.create_user_session(db, user.id, ip_address, user_agent)
        
        # Возвращаем токен
        return create_token_response(user, session.session_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка входа: {str(e)}"
        )

@router.post("/login-simple", response_model=Token)
async def login_user_simple(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Вход пользователя через простую форму
    
    **Параметры:**
    - `email`: Электронная почта
    - `password`: Пароль
    """
    try:
        # Аутентификация пользователя
        user = UserService.authenticate_user(db, email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Создаем новую сессию
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        session = UserService.create_user_session(db, user.id, ip_address, user_agent)
        
        # Возвращаем токен
        return create_token_response(user, session.session_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка входа: {str(e)}"
        )

@router.post("/login-form", response_model=Token)
async def login_user_form(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Вход пользователя через обычную форму
    
    **Параметры:**
    - `email`: Электронная почта
    - `password`: Пароль
    """
    try:
        # Аутентификация пользователя
        user = UserService.authenticate_user(db, email, password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        # Создаем новую сессию
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        session = UserService.create_user_session(db, user.id, ip_address, user_agent)
        
        # Возвращаем токен
        return create_token_response(user, session.session_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка входа: {str(e)}"
        )

@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Выход пользователя из системы"""
    try:
        # Получаем токен из заголовка
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            
            # Декодируем токен для получения session_token
            from app.services.auth_service import AuthService
            payload = AuthService.verify_token(token)
            if payload and "session" in payload:
                UserService.deactivate_session(db, payload["session"])
        
        return {"message": "Выход выполнен успешно"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка выхода: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Получение информации о текущем пользователе"""
    return user_to_response(current_user)

@router.get("/check")
async def check_auth_status(
    current_user: Optional[User] = Depends(get_current_user)
):
    """Проверка статуса аутентификации"""
    if current_user:
        return {
            "authenticated": True,
            "user": user_to_response(current_user)
        }
    else:
        return {
            "authenticated": False,
            "user": None
        }

@router.post("/cleanup-sessions")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Очистка истекших сессий (только для аутентифицированных пользователей)"""
    try:
        cleaned_count = UserService.cleanup_expired_sessions(db)
        return {
            "message": f"Очищено {cleaned_count} истекших сессий"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка очистки сессий: {str(e)}"
        ) 