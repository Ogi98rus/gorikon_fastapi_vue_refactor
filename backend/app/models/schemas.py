from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

# ============= ENUMS =============

class WeekDay(Enum):
    """Дни недели"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

# ============= БАЗОВЫЕ СХЕМЫ =============

class ResponseBase(BaseModel):
    """Базовая схема ответа"""
    success: bool = True
    message: str = "Операция выполнена успешно"
    
    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    """Схема ошибки"""
    message: str
    error_code: str
    timestamp: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ============= ENUM-Ы =============

class UserRoleEnum(str, Enum):
    """Роли пользователей"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    BANNED = "banned"

class UserStatusEnum(str, Enum):
    """Статусы пользователей"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"

class MathOperation(str, Enum):
    """Математические операции"""
    ADDITION = "+"
    SUBTRACTION = "-"
    MULTIPLICATION = "*"
    DIVISION = "/"

# ============= ПОЛЬЗОВАТЕЛИ =============

class UserCreate(BaseModel):
    """Создание пользователя"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    school_name: Optional[str] = Field(None, max_length=200)

class UserLogin(BaseModel):
    """Вход пользователя"""
    username: str  # email
    password: str

class UserResponse(BaseModel):
    """Ответ с информацией о пользователе"""
    id: int
    email: str
    full_name: str
    school_name: Optional[str] = None
    role: UserRoleEnum
    status: UserStatusEnum
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    banned_until: Optional[datetime] = None
    ban_reason: Optional[str] = None

class Token(BaseModel):
    """JWT токен"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    """Данные из токена"""
    username: Optional[str] = None

# ============= АДМИНИСТРИРОВАНИЕ ПОЛЬЗОВАТЕЛЕЙ =============

class UserListResponse(ResponseBase):
    """Список пользователей"""
    users: List[UserResponse]
    total_count: int
    page: int
    per_page: int

class UserAdminUpdate(BaseModel):
    """Обновление пользователя администратором"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    school_name: Optional[str] = Field(None, max_length=200)
    role: Optional[UserRoleEnum] = None
    status: Optional[UserStatusEnum] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserBanRequest(BaseModel):
    """Запрос на блокировку пользователя"""
    ban_duration_hours: Optional[int] = Field(None, ge=1, le=8760)  # До года
    ban_reason: str = Field(..., min_length=5, max_length=500)
    permanent: bool = False

class UserUnbanRequest(BaseModel):
    """Запрос на разблокировку пользователя"""
    reason: str = Field(..., min_length=5, max_length=500)

# ============= МАТЕМАТИЧЕСКИЙ ГЕНЕРАТОР =============

class MathGeneratorRequest(BaseModel):
    """Запрос к математическому генератору"""
    num_operands: int = Field(2, ge=2, le=5, description="Количество операндов")
    operations: List[MathOperation] = Field(..., min_items=1, description="Список операций")
    interval_start: int = Field(1, description="Начало интервала")
    interval_end: int = Field(100, description="Конец интервала")
    example_count: int = Field(10, ge=1, le=1000, description="Количество примеров")
    
    @validator('interval_end')
    def validate_interval(cls, v, values):
        if 'interval_start' in values and v <= values['interval_start']:
            raise ValueError('Конец интервала должен быть больше начала')
        return v

class MathGeneratorResponse(ResponseBase):
    """Ответ генератора математических примеров"""
    file_name: str
    examples_generated: int
    file_size: Optional[int] = None
    generation_id: Optional[int] = None  # ID генерации для авторизованных пользователей

# ============= КТП ГЕНЕРАТОР =============

class KTPGeneratorRequest(BaseModel):
    """Запрос к генератору КТП"""
    start_date: date = Field(..., description="Дата начала")
    end_date: date = Field(..., description="Дата окончания") 
    lessons_per_day: List[int] = Field(default=[1,1,1,1,1,0,0], description="Уроков по дням недели")
    file_name: str = Field(default="schedule", description="Имя файла")
    
    # Дни недели (понедельник = 0, воскресенье = 6)
    weekdays: List[int] = Field(
        default=[0, 1, 2, 3, 4], 
        description="Дни недели для занятий"
    )
    
    holidays: List[str] = Field(
        default=[], 
        description="Праздничные дни в формате 'дд.мм.гггг'"
    )
    
    vacation: List[str] = Field(
        default=[], 
        description="Дни каникул в формате 'дд.мм.гггг'"
    )

    @validator('lessons_per_day')
    def validate_lessons_per_day(cls, v):
        if len(v) != 7:
            raise ValueError('Должно быть 7 значений (по одному для каждого дня недели)')
        return v

    @validator('weekdays')
    def validate_weekdays(cls, v):
        for day in v:
            if not 0 <= day <= 6:
                raise ValueError('Дни недели должны быть от 0 до 6')
        return v

class KTPGeneratorResponse(BaseModel):
    """Ответ от генератора КТП"""
    file_name: str = Field(..., description="Имя сгенерированного файла")
    total_lessons: int = Field(..., description="Общее количество уроков")
    working_days: int = Field(..., description="Количество рабочих дней")
    file_size: int = Field(..., description="Размер файла в байтах")

    class Config:
        from_attributes = True

# ============= ИСТОРИЯ ГЕНЕРАЦИЙ =============

class GenerationInfo(BaseModel):
    """Информация о генерации"""
    id: int
    generator_type: str
    original_file_name: str
    file_size: int
    examples_generated: Optional[int] = None
    total_lessons: Optional[int] = None
    created_at: datetime
    download_count: int
    is_available: bool
    expires_at: Optional[datetime] = None
    parameters: dict

class GenerationListResponse(ResponseBase):
    """Список генераций пользователя"""
    generations: List[GenerationInfo]
    total_count: int
    page: int
    per_page: int

class GenerationDetailResponse(ResponseBase):
    """Детальная информация о генерации"""
    generation: GenerationInfo

# ============= АНАЛИТИКА =============

class GenerationStats(BaseModel):
    """Статистика генераций"""
    total_generations: int = 0
    math_generations: int = 0
    ktp_generations: int = 0
    unique_users: int = 0
    total_file_size: int = 0
    avg_processing_time: float = 0.0

class AnalyticsResponse(ResponseBase):
    """Ответ с аналитикой"""
    stats: GenerationStats
    period_start: date
    period_end: date

# ============= ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ =============

class UserProfileResponse(ResponseBase):
    """Расширенная информация о профиле пользователя"""
    user: UserResponse
    total_generations: int
    math_generations: int
    ktp_generations: int
    total_downloads: int
    account_age_days: int
    last_login: Optional[datetime] = None

class UpdateProfileRequest(BaseModel):
    """Обновление профиля пользователя"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    school_name: Optional[str] = Field(None, max_length=200)

class ChangePasswordRequest(BaseModel):
    """Смена пароля"""
    current_password: str
    new_password: str = Field(..., min_length=8)

# ============= БЕЗОПАСНОСТЬ =============

class SecurityStatsResponse(ResponseBase):
    """Статистика безопасности"""
    blocked_ips_count: int
    active_rate_limits: int
    recent_security_events: int
    event_types: dict
    total_security_logs: int

# ============= I18N =============

class LanguageResponse(ResponseBase):
    """Ответ с информацией о языке"""
    current_language: str
    available_languages: List[str]
    translations: dict

class TranslationUpdate(BaseModel):
    """Обновление перевода"""
    key: str
    value: str
    language: str 