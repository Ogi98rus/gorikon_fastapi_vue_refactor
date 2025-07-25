# Redis Integration для Rate Limiting

## Обзор

Добавлена поддержка Redis для хранения счетчиков rate limit вместо in-memory хранилища. Это обеспечивает:

- **Масштабируемость**: Rate limit работает между несколькими экземплярами приложения
- **Надежность**: Данные сохраняются при перезапуске
- **Производительность**: Быстрые операции с Redis
- **Fallback**: Автоматический переход к in-memory хранилищу при недоступности Redis

## Архитектура

### 1. Redis Service (`app/services/redis_service.py`)

```python
class RedisService:
    def increment_rate_limit(self, key: str, window_minutes: int = 1) -> Dict[str, Any]
    def get_rate_limit_info(self, key: str, window_minutes: int = 1) -> Dict[str, Any]
    def clear_rate_limit(self, key: str)
    def get_stats(self) -> Dict[str, Any]
```

### 2. Security Middleware

Обновлен `SecurityMiddleware` для использования Redis с fallback:

```python
def check_rate_limit_with_auth(self, ip: str, path: str, is_authenticated: bool) -> dict:
    # Пытаемся использовать Redis
    if redis_service.is_available():
        return self._redis_rate_limit(ip, path, is_authenticated, limit)
    else:
        # Fallback к in-memory
        return self._fallback_rate_limit(ip, path, is_authenticated, limit)
```

### 3. Docker Compose

Добавлен Redis сервис:

```yaml
redis:
  image: redis:7-alpine
  container_name: generator-redis
  ports:
    - "6379:6379"
  restart: unless-stopped
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
```

## Использование

### Запуск

1. **Запуск Redis:**
   ```bash
   docker-compose up redis -d
   ```

2. **Пересборка backend:**
   ```bash
   docker-compose build backend
   docker-compose restart backend
   ```

### API Endpoints

#### Получение статистики Redis
```http
GET /api/analytics/redis/stats
Authorization: Bearer <token>
```

#### Очистка rate limit
```http
POST /api/analytics/redis/clear-rate-limit
Authorization: Bearer <token>
Content-Type: application/json

{
  "key": "192.168.1.1:/api/ktp-generator"
}
```

### Ключи Redis

Формат ключей: `rate_limit:{ip}:{path}:{YYYY-MM-DDTHH:MM}`

Примеры:
- `rate_limit:192.168.1.1:/api/ktp-generator:2025-07-25T20:45`
- `rate_limit:172.18.0.1:/api/math-generator:2025-07-25T20:46`

### TTL (Time To Live)

- Ключи автоматически удаляются через 1 минуту
- Обеспечивает автоматическую очистку старых данных
- Экономит память Redis

## Конфигурация

### Настройки Redis

В `app/services/redis_service.py`:

```python
def __init__(self, host: str = "redis", port: int = 6379, db: int = 0):
    self.redis_client = redis.Redis(
        host=host,          # Имя сервиса в Docker Compose
        port=port,          # Стандартный порт Redis
        db=db,              # База данных 0
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
```

### Rate Limits

Лимиты остались прежними:

**Неавторизованные пользователи:**
- KTP/Math генераторы: 3 запроса/минуту
- Авторизация: 10 запросов/минуту
- Остальные API: 30 запросов/минуту

**Авторизованные пользователи:**
- KTP/Math генераторы: 1000 запросов/минуту
- Аналитика: 2000 запросов/минуту
- Остальные API: 1000 запросов/минуту

## Мониторинг

### Логирование

Redis операции логируются:

```
INFO: Redis подключение успешно
INFO: Redis недоступен, используем in-memory rate limiting
WARNING: Redis error, falling back to memory: Connection refused
```

### Статистика

Через API можно получить статистику Redis:

```json
{
  "redis_stats": {
    "connected_clients": 1,
    "used_memory_human": "1.23M",
    "total_commands_processed": 1234,
    "keyspace_hits": 567,
    "keyspace_misses": 89
  },
  "redis_available": true
}
```

## Fallback механизм

При недоступности Redis система автоматически переключается на in-memory хранилище:

1. **Проверка доступности:** `redis_service.is_available()`
2. **Fallback:** `_fallback_rate_limit()` метод
3. **Логирование:** Информация о переключении
4. **Прозрачность:** Пользователи не замечают переключения

## Преимущества

### По сравнению с in-memory:

✅ **Масштабируемость** - работает с несколькими экземплярами  
✅ **Надежность** - данные сохраняются при перезапуске  
✅ **Мониторинг** - детальная статистика использования  
✅ **Управление** - возможность очистки rate limit через API  
✅ **Производительность** - быстрые операции Redis  

### По сравнению с другими решениями:

✅ **Простота** - минимальная конфигурация  
✅ **Fallback** - автоматический переход к in-memory  
✅ **Гибкость** - легко изменить логику rate limiting  
✅ **Отладка** - подробное логирование  

## Тестирование

### Тест подключения

```bash
python test_redis.py
```

### Тест rate limit

```bash
# Без авторизации (должен сработать лимит)
curl -X POST http://localhost:8000/api/ktp-generator \
  -H "Content-Type: multipart/form-data" \
  -F "start_date=2024-09-01" \
  -F "end_date=2025-05-31"

# С авторизацией (высокий лимит)
curl -X POST http://localhost:8000/api/ktp-generator \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: multipart/form-data" \
  -F "start_date=2024-09-01" \
  -F "end_date=2025-05-31"
```

## Устранение неполадок

### Redis не подключается

1. **Проверьте статус контейнера:**
   ```bash
   docker-compose ps redis
   ```

2. **Проверьте логи:**
   ```bash
   docker-compose logs redis
   ```

3. **Перезапустите Redis:**
   ```bash
   docker-compose restart redis
   ```

### Backend не видит Redis

1. **Проверьте зависимости в docker-compose.yml:**
   ```yaml
   backend:
     depends_on:
       - mysql
       - redis  # Должно быть!
   ```

2. **Пересоберите backend:**
   ```bash
   docker-compose build backend
   docker-compose restart backend
   ```

### Fallback не работает

1. **Проверьте логи backend:**
   ```bash
   docker-compose logs backend | grep -i redis
   ```

2. **Проверьте подключение:**
   ```bash
   docker exec -it generator-backend python -c "
   from app.services.redis_service import redis_service
   print('Redis available:', redis_service.is_available())
   "
   ```

## Заключение

Redis интеграция обеспечивает надежное и масштабируемое решение для rate limiting с автоматическим fallback к in-memory хранилищу. Система остается работоспособной даже при недоступности Redis. 