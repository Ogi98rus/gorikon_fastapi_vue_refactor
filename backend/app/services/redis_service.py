import redis
import json
import logging
from typing import Optional, Any, Dict
from app.core.config import settings
from app.services.fallback_cache import fallback_cache

logger = logging.getLogger(__name__)

class RedisService:
    """Сервис для работы с Redis с fallback на in-memory кеш"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379')
        self.use_fallback = False
    
    def connect(self):
        """Подключение к Redis"""
        try:
            # Парсим URL Redis
            if self.redis_url.startswith('redis://'):
                # Убираем redis:// и парсим
                url_parts = self.redis_url.replace('redis://', '').split(':')
                host = url_parts[0] if url_parts[0] else 'localhost'
                port = int(url_parts[1]) if len(url_parts) > 1 else 6379
                
                self.redis = redis.Redis(
                    host=host,
                    port=port,
                    decode_responses=True,
                    max_connections=20,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
            else:
                # Fallback для localhost
                self.redis = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True,
                    max_connections=20
                )
            
            # Проверяем подключение
            self.redis.ping()
            self.use_fallback = False
            logger.info("✅ Подключение к Redis установлено")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            self.redis = None
            self.use_fallback = True
            logger.info("🔄 Используется fallback in-memory кеш")
    
    def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            self.redis.close()
            logger.info("🔌 Отключение от Redis")
    
    def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Установка значения в кеш"""
        if self.use_fallback or not self.redis:
            return fallback_cache.set_cache(key, value, expire)
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка установки кеша в Redis: {e}")
            # Fallback на in-memory кеш
            self.use_fallback = True
            return fallback_cache.set_cache(key, value, expire)
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Получение значения из кеша"""
        if self.use_fallback or not self.redis:
            return fallback_cache.get_cache(key)
        
        try:
            value = self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения кеша из Redis: {e}")
            # Fallback на in-memory кеш
            self.use_fallback = True
            return fallback_cache.get_cache(key)
    
    def delete_cache(self, key: str) -> bool:
        """Удаление значения из кеша"""
        if self.use_fallback or not self.redis:
            return fallback_cache.delete_cache(key)
        
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления кеша из Redis: {e}")
            # Fallback на in-memory кеш
            self.use_fallback = True
            return fallback_cache.delete_cache(key)
    
    def set_session(self, session_id: str, data: Dict[str, Any], expire: int = 86400) -> bool:
        """Установка сессии пользователя"""
        return self.set_cache(f"session:{session_id}", data, expire)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение сессии пользователя"""
        return self.get_cache(f"session:{session_id}")
    
    def delete_session(self, session_id: str) -> bool:
        """Удаление сессии пользователя"""
        return self.delete_cache(f"session:{session_id}")
    
    def increment_counter(self, key: str, expire: int = 60) -> int:
        """Инкремент счетчика для rate limiting"""
        if self.use_fallback or not self.redis:
            return fallback_cache.increment_counter(key, expire)
        
        try:
            # Используем pipeline для атомарности операций
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, expire)
            result = pipe.execute()
            return result[0]
        except Exception as e:
            logger.error(f"❌ Ошибка инкремента счетчика в Redis: {e}")
            # Fallback на in-memory кеш
            self.use_fallback = True
            return fallback_cache.increment_counter(key, expire)
    
    def get_counter(self, key: str) -> int:
        """Получение значения счетчика"""
        if self.use_fallback or not self.redis:
            return fallback_cache.get_counter(key)
        
        try:
            value = self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"❌ Ошибка получения счетчика из Redis: {e}")
            # Fallback на in-memory кеш
            self.use_fallback = True
            return fallback_cache.get_counter(key)
    
    def health_check(self) -> bool:
        """Проверка здоровья Redis"""
        if self.use_fallback:
            return fallback_cache.health_check()
        
        if not self.redis:
            return False
        
        try:
            self.redis.ping()
            return True
        except Exception:
            self.use_fallback = True
            return fallback_cache.health_check()

# Глобальный экземпляр Redis сервиса
redis_service = RedisService() 