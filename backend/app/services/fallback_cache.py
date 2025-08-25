import logging
import time
from typing import Optional, Any, Dict
from collections import OrderedDict

logger = logging.getLogger(__name__)

class FallbackCache:
    """Простой in-memory кеш как fallback для Redis"""
    
    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.expiry_times = {}
    
    def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Установка значения в кеш"""
        try:
            # Удаляем старые записи
            self._cleanup_expired()
            
            # Проверяем размер кеша
            if len(self.cache) >= self.max_size:
                # Удаляем самую старую запись
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                if oldest_key in self.expiry_times:
                    del self.expiry_times[oldest_key]
            
            # Добавляем новую запись
            self.cache[key] = value
            self.expiry_times[key] = time.time() + expire
            
            # Перемещаем в конец (LRU)
            self.cache.move_to_end(key)
            
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка установки кеша: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[Any]:
        """Получение значения из кеша"""
        try:
            # Проверяем срок действия
            if key in self.expiry_times and time.time() > self.expiry_times[key]:
                # Удаляем просроченную запись
                del self.cache[key]
                del self.expiry_times[key]
                return None
            
            if key in self.cache:
                # Перемещаем в конец (LRU)
                self.cache.move_to_end(key)
                return self.cache[key]
            
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка получения кеша: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Удаление значения из кеша"""
        try:
            if key in self.cache:
                del self.cache[key]
            if key in self.expiry_times:
                del self.expiry_times[key]
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления кеша: {e}")
            return False
    
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
        try:
            current_value = self.get_cache(key) or 0
            new_value = current_value + 1
            self.set_cache(key, new_value, expire)
            return new_value
        except Exception as e:
            logger.error(f"❌ Ошибка инкремента счетчика: {e}")
            return 0
    
    def get_counter(self, key: str) -> int:
        """Получение значения счетчика"""
        try:
            value = self.get_cache(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"❌ Ошибка получения счетчика: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Проверка здоровья кеша"""
        return True
    
    def _cleanup_expired(self):
        """Очистка просроченных записей"""
        current_time = time.time()
        expired_keys = [
            key for key, expiry in self.expiry_times.items() 
            if current_time > expiry
        ]
        
        for key in expired_keys:
            if key in self.cache:
                del self.cache[key]
            if key in self.expiry_times:
                del self.expiry_times[key]

# Глобальный экземпляр fallback кеша
fallback_cache = FallbackCache()
