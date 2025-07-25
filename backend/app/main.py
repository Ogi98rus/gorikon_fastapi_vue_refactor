from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from pathlib import Path

# Добавляем путь к app в sys.path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Импорты приложения
from app.core.config import settings
from app.models.database import get_db, create_tables
from app.middleware.security import SecurityMiddleware
from app.middleware.i18n import I18nMiddleware

# Импорт роутеров
from app.routers import auth, analytics, i18n, security, math, ktp, test_file
from app.routers import user_history, admin
from app.models.schemas import ErrorResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🎓 **Генератор учебных материалов**
    
    Простой и надежный инструмент для создания образовательного контента:
    
    ## 📊 Математический генератор
    - Арифметические примеры с настраиваемыми параметрами
    - Поддержка основных операций (+, -, *, /)
    - Гибкие диапазоны чисел и количество операндов
    - Автоматическая генерация PDF с ответами
    
    ## 📅 КТП генератор
    - Календарно-тематическое планирование
    - Учет праздников и каникул
    - Настройка рабочих дней и количества уроков
    - Экспорт в Excel с форматированием дат
    
    ## 🔧 Возможности
    - REST API с валидацией данных
    - Автоматическая генерация документации
    - Обработка ошибок и логирование
    - Модульная архитектура для легкого расширения
    """,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None
)

# Добавляем middleware (порядок важен! Последний добавленный выполняется первым)
# Поэтому сначала добавляем Security и I18n, а CORS в самом конце

# Добавляем улучшенный security middleware
security_middleware_instance = SecurityMiddleware(app)
app.add_middleware(SecurityMiddleware)

# Добавляем i18n middleware
app.add_middleware(I18nMiddleware)

# CORS должен быть добавлен ПОСЛЕДНИМ, чтобы выполняться ПЕРВЫМ!
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Подключение роутеров
app.include_router(i18n.router)      # Интернационализация
app.include_router(auth.router)      # Аутентификация
app.include_router(analytics.router) # Аналитика
app.include_router(security.router)  # Безопасность
app.include_router(math.router)      # Математический генератор
app.include_router(ktp.router)       # КТП генератор
app.include_router(user_history.router)  # История генераций пользователя
app.include_router(admin.router)     # Администрирование пользователей

# Legacy роутеры для совместимости
app.include_router(math.legacy_router)  # Математический генератор (Legacy)
app.include_router(ktp.legacy_router)   # КТП генератор (Legacy)

# Инициализируем security middleware в роутере
security.set_security_middleware(security_middleware_instance)

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Обработка HTTP ошибок"""
    error_response = ErrorResponse(
        message=exc.detail,
        error_code=f"HTTP_{exc.status_code}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Обработка ошибок валидации"""
    error_response = ErrorResponse(
        message=f"Ошибка валидации: {str(exc)}",
        error_code="VALIDATION_ERROR"
    )
    return JSONResponse(
        status_code=400,
        content=error_response.dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Обработка общих ошибок"""
    logger.error(f"Необработанная ошибка: {str(exc)}", exc_info=True)
    
    error_response = ErrorResponse(
        message="Внутренняя ошибка сервера",
        error_code="INTERNAL_ERROR",
        details={"error": str(exc)} if settings.debug else None
    )
    return JSONResponse(
        status_code=500,
        content=error_response.dict()
    )

# Основные эндпоинты
@app.get("/", tags=["Система"])
async def root():
    """Корневой эндпоинт с информацией о приложении"""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs_url": "/docs" if settings.debug else "disabled",
        "endpoints": {
            "i18n": "/api/i18n",
            "auth": "/api/auth",
            "analytics": "/api/analytics",
            "security": "/api/security",
            "math_generator": "/api/math/generate",
            "ktp_generator": "/api/ktp/generate"
        },
        "features": [
            "🌍 Мультиязычная поддержка (5 языков)",
            "👤 Система аутентификации пользователей",
            "📊 Аналитика и статистика использования",
            "🔒 Многоуровневая система безопасности",
            "🧮 Математические примеры с настраиваемыми параметрами",
            "📅 Календарно-тематическое планирование", 
            "✅ Валидация входных данных",
            "🔧 Автоматическая обработка ошибок",
            "🏗️ Модульная архитектура"
        ]
    }

@app.get("/health", tags=["Система"])
async def health_check():
    """Проверка состояния приложения"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "components": {
            "database": "connected",
            "i18n": "multilingual",
            "auth": "enabled",
            "analytics": "enabled",
            "security": "protected",
            "generators": "ready"
        },
        "config": {
            "debug": settings.debug,
            "max_operands": settings.max_operands,
            "max_examples": settings.max_examples,
            "max_lessons_per_day": settings.max_lessons_per_day
        }
    }

@app.get("/api/info", tags=["API"])
async def api_info():
    """Информация об API"""
    return {
        "api_version": "2.0",
        "generators": {
            "math": {
                "endpoint": "/api/math/generate",
                "parameters": ["num_operands", "operations", "interval_start", "interval_end", "example_count"],
                "operations": ["+", "-", "*", "/"],
                "output_format": "PDF"
            },
            "ktp": {
                "endpoint": "/api/ktp/generate", 
                "parameters": ["start_date", "end_date", "weekdays", "lessons_per_day", "holidays", "vacation", "file_name"],
                "output_format": "Excel"
            }
        },
        "legacy_support": {
            "math": "/api/math/math-generator",
            "ktp": "/api/ktp/ktp-generator"
        }
    }

# Событие запуска
@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    logger.info(f"🚀 Запуск {settings.app_name} v{settings.app_version}")
    logger.info(f"🔧 Режим отладки: {settings.debug}")
    logger.info(f"📁 Временная папка: {settings.temp_dir}")
    
    # Инициализация базы данных
    try:
        create_tables()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
    
    logger.info(f"⚙️ Настройки загружены из .env")
    logger.info(f"🎯 Доступные функции: аутентификация, аналитика, генераторы")

# Событие остановки  
@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    logger.info(f"🛑 Остановка {settings.app_name}")

# Кастомизация OpenAPI схемы
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.app_name,
        version=settings.app_version,
        description=app.description,
        routes=app.routes,
    )
    
    # Добавляем дополнительную информацию
    openapi_schema["info"]["contact"] = {
        "name": "Команда разработки",
        "url": "https://generator.gorikon.ru",
    }
    
    openapi_schema["info"]["license"] = {
        "name": "MIT License",
    }
    
    # Добавляем теги
    openapi_schema["tags"] = [
        {
            "name": "Интернационализация",
            "description": "Мультиязычная поддержка и управление переводами"
        },
        {
            "name": "Аутентификация",
            "description": "Регистрация, вход и управление пользователями"
        },
        {
            "name": "Аналитика",
            "description": "Статистика использования и дашборд"
        },
        {
            "name": "Безопасность",
            "description": "Мониторинг безопасности и управление защитой"
        },
        {
            "name": "Математический генератор",
            "description": "Создание математических примеров"
        },
        {
            "name": "КТП генератор", 
            "description": "Генерация календарно-тематического планирования"
        },
        {
            "name": "Система",
            "description": "Системная информация и проверки состояния"
        },
        {
            "name": "API",
            "description": "Информация об API и его возможностях"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    ) 