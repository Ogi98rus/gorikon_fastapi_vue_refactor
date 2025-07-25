from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import secrets
import string

from app.core.config import settings
from app.models.database import User, UserSession
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Сервис аутентификации и авторизации"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Создание JWT токена"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Проверка и декодирование JWT токена"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def generate_session_token() -> str:
        """Генерация случайного токена сессии"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))

class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Создание нового пользователя"""
        # Проверяем, существует ли пользователь
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Создаем нового пользователя
        hashed_password = AuthService.hash_password(user_data.password)
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            school_name=user_data.school_name,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        
        # Обновляем время последнего входа
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user_session(db: Session, user_id: int, ip_address: str, user_agent: str) -> UserSession:
        """Создание пользовательской сессии"""
        session_token = AuthService.generate_session_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)  # Сессия на 24 часа
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def get_active_session(db: Session, session_token: str) -> Optional[UserSession]:
        """Получение активной сессии"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True,
            UserSession.expires_at > datetime.utcnow()
        ).first()
        
        if session:
            # Обновляем время последней активности
            session.last_activity = datetime.utcnow()
            db.commit()
        
        return session
    
    @staticmethod
    def deactivate_session(db: Session, session_token: str) -> bool:
        """Деактивация сессии (выход)"""
        session = db.query(UserSession).filter(
            UserSession.session_token == session_token
        ).first()
        
        if session:
            session.is_active = False
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def cleanup_expired_sessions(db: Session) -> int:
        """Очистка истекших сессий"""
        expired_count = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow()
        ).update({"is_active": False})
        
        db.commit()
        return expired_count

def create_token_response(user: User, session_token: str) -> Token:
    """Создание ответа с токеном"""
    # Создаем JWT токен с данными пользователя
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "session": session_token
    }
    
    access_token = AuthService.create_access_token(token_data)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=user_to_response(user)
    )

def user_to_response(user: User) -> UserResponse:
    """Преобразование модели пользователя в ответ"""
    from app.models.schemas import UserRoleEnum, UserStatusEnum
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        school_name=user.school_name,
        role=UserRoleEnum.USER,  # Упрощенно, всегда USER
        status=UserStatusEnum.ACTIVE,  # Упрощенно, всегда ACTIVE
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        last_login=user.last_login,
        banned_until=None,  # Пока не используется
        ban_reason=None  # Пока не используется
    ) 