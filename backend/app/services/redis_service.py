import redis
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RedisService:
    """Сервис для работы с Redis"""
    
    def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        self._test_connection()
    
    def _test_connection(self):
        """Тестируем подключение к Redis"""
        try:
            self.redis_client.ping()
            logger.info("✅ Redis подключение успешно")
        except redis.ConnectionError as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            # Fallback к in-memory хранилищу
            self.redis_client = None
    
    def is_available(self) -> bool:
        """Проверяем доступность Redis"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def increment_rate_limit(self, key: str, window_minutes: int = 1) -> Dict[str, Any]:
        """
        Увеличиваем счетчик rate limit для ключа
        
        Args:
            key: Ключ для rate limit (например, "ip:192.168.1.1:path:/api/ktp-generator")
            window_minutes: Окно времени в минутах
            
        Returns:
            Dict с информацией о текущем состоянии rate limit
        """
        if not self.is_available():
            return {"error": "Redis недоступен"}
        
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            # Создаем ключ с временной меткой
            current_minute = now.strftime("%Y-%m-%dT%H:%M")
            redis_key = f"rate_limit:{key}:{current_minute}"
            
            # Увеличиваем счетчик
            current_count = self.redis_client.incr(redis_key)
            
            # Устанавливаем TTL для автоматической очистки
            if current_count == 1:
                self.redis_client.expire(redis_key, window_minutes * 60)
            
            # Получаем все ключи для этого IP/path в текущем окне
            pattern = f"rate_limit:{key}:*"
            all_keys = self.redis_client.keys(pattern)
            
            # Подсчитываем общее количество запросов в окне
            total_requests = 0
            for k in all_keys:
                count = self.redis_client.get(k)
                if count:
                    total_requests += int(count)
            
            return {
                "current_count": current_count,
                "total_requests": total_requests,
                "window_start": window_start.isoformat(),
                "window_end": now.isoformat(),
                "redis_key": redis_key
            }
            
        except Exception as e:
            logger.error(f"Ошибка при работе с Redis rate limit: {e}")
            return {"error": str(e)}
    
    def get_rate_limit_info(self, key: str, window_minutes: int = 1) -> Dict[str, Any]:
        """
        Получаем информацию о rate limit для ключа
        
        Args:
            key: Ключ для rate limit
            window_minutes: Окно времени в минутах
            
        Returns:
            Dict с информацией о rate limit
        """
        if not self.is_available():
            return {"error": "Redis недоступен"}
        
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=window_minutes)
            
            # Получаем все ключи для этого IP/path в текущем окне
            pattern = f"rate_limit:{key}:*"
            all_keys = self.redis_client.keys(pattern)
            
            # Подсчитываем общее количество запросов в окне
            total_requests = 0
            oldest_request = None
            
            for k in all_keys:
                count = self.redis_client.get(k)
                if count:
                    total_requests += int(count)
                    
                    # Извлекаем время из ключа
                    try:
                        time_str = k.split(":")[-1]
                        request_time = datetime.fromisoformat(time_str)
                        if oldest_request is None or request_time < oldest_request:
                            oldest_request = request_time
                    except:
                        pass
            
            return {
                "total_requests": total_requests,
                "window_start": window_start.isoformat(),
                "window_end": now.isoformat(),
                "oldest_request": oldest_request.isoformat() if oldest_request else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о rate limit: {e}")
            return {"error": str(e)}
    
    def clear_rate_limit(self, key: str):
        """Очищаем rate limit для ключа"""
        if not self.is_available():
            return
        
        try:
            pattern = f"rate_limit:{key}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Очищен rate limit для ключа: {key}")
        except Exception as e:
            logger.error(f"Ошибка при очистке rate limit: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получаем статистику Redis"""
        if not self.is_available():
            return {"error": "Redis недоступен"}
        
        try:
            info = self.redis_client.info()
            return {
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "N/A"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статистики Redis: {e}")
            return {"error": str(e)}

# Глобальный экземпляр Redis сервиса
redis_service = RedisService() 