import aioredis
import json
import logging
from typing import Optional, Any, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    """Сервис для работы с Redis"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379')
    
    async def connect(self):
        """Подключение к Redis"""
        try:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20
            )
            await self.redis.ping()
            logger.info("✅ Подключение к Redis установлено")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Redis: {e}")
            self.redis = None
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("🔌 Отключение от Redis")
    
    async def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Установка значения в кеш"""
        if not self.redis:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка установки кеша: {e}")
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Получение значения из кеша"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения кеша: {e}")
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """Удаление значения из кеша"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления кеша: {e}")
            return False
    
    async def set_session(self, session_id: str, data: Dict[str, Any], expire: int = 86400) -> bool:
        """Установка сессии пользователя"""
        return await self.set_cache(f"session:{session_id}", data, expire)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Получение сессии пользователя"""
        return await self.get_cache(f"session:{session_id}")
    
    async def delete_session(self, session_id: str) -> bool:
        """Удаление сессии пользователя"""
        return await self.delete_cache(f"session:{session_id}")
    
    async def increment_counter(self, key: str, expire: int = 60) -> int:
        """Инкремент счетчика для rate limiting"""
        if not self.redis:
            return 0
        
        try:
            # Используем pipeline для атомарности операций
            async with self.redis.pipeline() as pipe:
                await pipe.incr(key)
                await pipe.expire(key, expire)
                result = await pipe.execute()
                return result[0]
        except Exception as e:
            logger.error(f"❌ Ошибка инкремента счетчика: {e}")
            return 0
    
    async def get_counter(self, key: str) -> int:
        """Получение значения счетчика"""
        if not self.redis:
            return 0
        
        try:
            value = await self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"❌ Ошибка получения счетчика: {e}")
            return 0
    
    async def health_check(self) -> bool:
        """Проверка здоровья Redis"""
        if not self.redis:
            return False
        
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False

# Глобальный экземпляр Redis сервиса
redis_service = RedisService() 