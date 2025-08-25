from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

async def rate_limit_middleware(request: Request, call_next):
    """Middleware для ограничения количества запросов"""
    
    # Получаем IP адрес клиента
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path
    
    # Создаем ключ для rate limiting
    rate_limit_key = f"rate_limit:{client_ip}:{path}"
    
    try:
        # Проверяем текущий счетчик
        current_count = redis_service.get_counter(rate_limit_key)
        
        if current_count >= 60:  # 60 запросов в минуту
            # Превышен лимит запросов
            logger.warning(f"Rate limit exceeded for {client_ip} on {path}: {current_count} requests")
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "message": "Превышен лимит запросов. Максимум 60 запросов в минуту.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Увеличиваем счетчик
        redis_service.increment_counter(rate_limit_key, expire=60)
        
        # Добавляем заголовки с информацией о rate limit
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = "60"
        response.headers["X-RateLimit-Remaining"] = str(max(0, 60 - current_count - 1))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
        
    except Exception as e:
        logger.error(f"Error in rate limiting middleware: {e}")
        # В случае ошибки пропускаем запрос
        return await call_next(request)
