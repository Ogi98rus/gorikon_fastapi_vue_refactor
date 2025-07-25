from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db, User
from app.services.auth_service import AuthService, UserService

# Настройка Bearer токенов
security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Получение текущего пользователя из JWT токена
    Возвращает None если пользователь не аутентифицирован
    """
    if not credentials:
        return None
    
    # Проверяем JWT токен
    payload = AuthService.verify_token(credentials.credentials)
    if not payload:
        return None
    
    # Получаем ID пользователя из токена
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Проверяем сессию
    session_token = payload.get("session")
    if session_token:
        session = UserService.get_active_session(db, session_token)
        if not session:
            return None
    
    # Получаем пользователя из базы данных
    user = UserService.get_user_by_id(db, int(user_id))
    if not user or not user.is_active:
        return None
    
    return user

async def get_current_active_user(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    Получение текущего активного пользователя
    Вызывает исключение если пользователь не аутентифицирован
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима аутентификация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Получение текущего суперпользователя
    Вызывает исключение если пользователь не является суперпользователем
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа"
        )
    return current_user

def get_client_ip(request: Request) -> str:
    """Получение IP адреса клиента"""
    # Проверяем заголовки от прокси серверов
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback на адрес из клиента
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Получение User-Agent клиента"""
    return request.headers.get("User-Agent", "unknown") 