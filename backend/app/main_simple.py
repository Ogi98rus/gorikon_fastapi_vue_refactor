from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Добавляем путь к app в sys.path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Импорты приложения
from app.core.config import settings
from app.middleware.i18n import I18nMiddleware

# Импорт роутеров
from app.routers import i18n, math, ktp, math_game
from app.models.schemas import ErrorResponse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus метрики
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

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
# Добавляем i18n middleware
app.add_middleware(I18nMiddleware)

# CORS должен быть добавлен ПОСЛЕДНИМ, чтобы выполняться ПЕРВЫМ!
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", 
        "http://127.0.0.1:8080", 
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://gorikon.ru",
        "http://gorikon.ru"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(i18n.router)      # Интернационализация
app.include_router(math.router)      # Математический генератор
app.include_router(ktp.router)       # КТП генератор
app.include_router(math_game.router) # Математическая игра
app.include_router(math.legacy_router)  # Legacy математический генератор
app.include_router(ktp.legacy_router)   # Legacy КТП генератор

# События жизненного цикла приложения
@app.on_event("startup")
async def startup_event():
    """Событие запуска приложения"""
    logger.info("🚀 Запуск приложения...")
    logger.info("✅ Приложение запущено успешно")

@app.on_event("shutdown")
async def shutdown_event():
    """Событие остановки приложения"""
    logger.info("🛑 Остановка приложения...")
    logger.info("✅ Приложение остановлено")

# Middleware для сбора метрик
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware для сбора метрик Prometheus"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Записываем метрики
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

# Эндпоинт для метрик Prometheus
@app.get("/metrics")
async def metrics():
    """Эндпоинт для метрик Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Эндпоинт для проверки здоровья
@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "app": "healthy"
        }
    }

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
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
