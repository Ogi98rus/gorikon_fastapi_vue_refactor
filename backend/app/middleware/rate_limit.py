from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import logging
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

class RateLimitMiddleware:
    """Middleware для ограничения количества запросов"""
    
    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 100):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
    
    async def __call__(self, request: Request, call_next):
        # Получаем IP адрес клиента
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # Создаем ключ для rate limiting
        rate_limit_key = f"rate_limit:{client_ip}:{path}"
        
        try:
            # Проверяем текущий счетчик
            current_count = await redis_service.get_counter(rate_limit_key)
            
            if current_count >= self.requests_per_minute:
                # Превышен лимит запросов
                logger.warning(f"Rate limit exceeded for {client_ip} on {path}: {current_count} requests")
                
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too Many Requests",
                        "message": f"Превышен лимит запросов. Максимум {self.requests_per_minute} запросов в минуту.",
                        "retry_after": 60
                    },
                    headers={"Retry-After": "60"}
                )
            
            # Увеличиваем счетчик
            await redis_service.increment_counter(rate_limit_key, expire=60)
            
            # Добавляем заголовки с информацией о rate limit
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests_per_minute - current_count - 1))
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in rate limiting middleware: {e}")
            # В случае ошибки пропускаем запрос
            return await call_next(request)

# Глобальный экземпляр middleware
rate_limit_middleware = RateLimitMiddleware()
