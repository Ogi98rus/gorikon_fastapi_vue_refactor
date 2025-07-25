from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
from datetime import datetime, timedelta
import time
import re
import hashlib
import secrets
from typing import Dict, Set, Optional
import logging
import traceback

from app.core.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Безопасный middleware для обеспечения безопасности"""
    
    def __init__(self, app):
        super().__init__(app)
        
        # Rate limiting
        self.rate_limits = defaultdict(deque)  # IP -> список временных меток
        self.blocked_ips = {}  # IP -> время блокировки
        
        # Защита от атак (исключаем нормальные URL параметры)
        self.suspicious_patterns = [
            r'<script[^>]*>.*?</script>',  # XSS
            r'javascript\s*:',  # XSS  
            r'on\w+\s*=\s*["\'][^"\']*["\']',  # Event handlers
            r'union\s+select\s+',  # SQL injection
            r'drop\s+table\s+',  # SQL injection
            r'insert\s+into\s+',  # SQL injection
            r'\.\./\.\./\.\.',  # Path traversal (3+ levels)
            r'etc/passwd',  # Path traversal
            r'cmd\.exe',  # Command injection
            r'/bin/(sh|bash)\s',  # Command injection
            r'eval\s*\(',  # Code injection
            r'exec\s*\(',  # Code injection
        ]
        
        try:
            self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
        except Exception as e:
            logger.error(f"Ошибка компиляции паттернов безопасности: {e}")
            self.compiled_patterns = []
        
        # CSRF защита
        self.csrf_tokens = set()
        
        # Логирование подозрительной активности
        self.security_log = deque(maxlen=1000)

    async def dispatch(self, request: Request, call_next):
        """Основная логика middleware с улучшенной обработкой ошибок"""
        
        # Пропускаем OPTIONS запросы без проверок (для CORS)
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        # Пропускаем некоторые пути без rate limiting
        excluded_paths = ["/docs", "/redoc", "/openapi.json", "/favicon.ico", "/health"]
        if any(str(request.url.path).startswith(path) for path in excluded_paths):
            response = await call_next(request)
            return response
        
        # Получаем IP клиента безопасно
        try:
            client_ip = self.get_client_ip(request)
        except Exception as e:
            logger.error(f"Ошибка получения IP клиента: {e}")
            client_ip = "unknown"
        
        try:
            # 1. Проверяем заблокированные IP
            if self.is_ip_blocked(client_ip):
                return self.create_security_response(
                    "IP адрес временно заблокирован",
                    status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # 2. Проверяем аутентификацию пользователя
            is_authenticated = self.check_user_authentication(request)
            
            # 3. Rate limiting (с защитой от ошибок и учетом аутентификации)
            try:
                rate_limit_result = self.check_rate_limit_with_auth(
                    client_ip, 
                    str(request.url.path) if request.url else "/",
                    is_authenticated
                )
                
                if not rate_limit_result["allowed"]:
                    logger.info(f"Rate limit exceeded - IP: {client_ip}, Path: {request.url.path}, Auth: {is_authenticated}, Limit: {rate_limit_result.get('limit', 'N/A')}")
                    self.log_security_event(client_ip, "RATE_LIMIT_EXCEEDED", str(request.url))
                    return self.create_rate_limit_response(rate_limit_result, is_authenticated)
            except Exception as e:
                logger.warning(f"Ошибка проверки rate limit: {e}")
                # Продолжаем выполнение, не блокируем запрос
            
            # 3. Проверяем размер запроса (с защитой от ошибок)
            try:
                content_length = int(request.headers.get("content-length", "0"))
                if content_length > settings.max_file_size:
                    self.log_security_event(client_ip, "LARGE_REQUEST", f"Size: {content_length}")
                    return self.create_security_response(
                        "Размер запроса слишком большой",
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                    )
            except (ValueError, TypeError) as e:
                logger.warning(f"Ошибка проверки размера запроса: {e}")
                # Продолжаем выполнение
            
            # 4. Проверяем подозрительные паттерны в URL (с защитой от ошибок)
            try:
                if self.detect_malicious_patterns(str(request.url)):
                    self.log_security_event(client_ip, "MALICIOUS_URL", str(request.url))
                    return self.create_security_response(
                        "Обнаружена подозрительная активность",
                        status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                logger.warning(f"Ошибка проверки вредоносных паттернов: {e}")
                # Продолжаем выполнение
            
            # 5. Проверяем User-Agent (с защитой от ошибок)
            try:
                user_agent = request.headers.get("user-agent", "")
                if not self.is_valid_user_agent(user_agent):
                    self.log_security_event(client_ip, "SUSPICIOUS_USER_AGENT", user_agent)
                    # Логируем, но не блокируем
            except Exception as e:
                logger.warning(f"Ошибка проверки User-Agent: {e}")
                # Продолжаем выполнение
            
            # 6. Выполняем запрос
            start_time = time.time()
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # 7. Добавляем security headers (с защитой от ошибок)
            try:
                response = self.add_security_headers(response)
            except Exception as e:
                logger.warning(f"Ошибка добавления security headers: {e}")
                # Продолжаем выполнение без headers
            
            # 8. Логируем запрос (с защитой от ошибок)
            try:
                self.log_request(client_ip, request, response, processing_time)
            except Exception as e:
                logger.warning(f"Ошибка логирования запроса: {e}")
                # Продолжаем выполнение без логирования
            
            return response
            
        except Exception as e:
            # Подробное логирование ошибки
            error_trace = traceback.format_exc()
            logger.error(f"Критическая ошибка в SecurityMiddleware: {e}\nТрассировка: {error_trace}")
            
            try:
                self.log_security_event(client_ip, "MIDDLEWARE_ERROR", f"{str(e)[:200]}...")
            except:
                pass  # Если даже логирование не работает
            
            # Возвращаем безопасный ответ об ошибке
            return self.create_security_response(
                "Внутренняя ошибка сервера",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_client_ip(self, request: Request) -> str:
        """Безопасное получение IP адреса клиента"""
        try:
            # Проверяем заголовки от прокси
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            
            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                return real_ip
            
            # Fallback на прямой IP
            if request.client and hasattr(request.client, 'host'):
                return request.client.host
            
            return "unknown"
        except Exception as e:
            logger.warning(f"Ошибка получения IP клиента: {e}")
            return "unknown"

    def check_user_authentication(self, request: Request) -> bool:
        """Проверяем аутентифицирован ли пользователь"""
        try:
            # Проверяем Authorization header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                logger.debug(f"Найден Bearer токен для {request.url.path}")
                return True
                
            # Проверяем cookie с токеном (если используется)
            token_cookie = request.cookies.get("access_token")
            if token_cookie:
                logger.debug(f"Найден cookie токен для {request.url.path}")
                return True
            
            logger.debug(f"Токен не найден для {request.url.path}, headers: {list(request.headers.keys())}")
            return False
        except Exception as e:
            logger.warning(f"Ошибка проверки аутентификации: {e}")
            return False

    def check_rate_limit_with_auth(self, ip: str, path: str, is_authenticated: bool) -> dict:
        """Проверка лимита запросов с учетом аутентификации и Redis"""
        try:
            # Устанавливаем лимиты в зависимости от аутентификации
            if is_authenticated:
                # Для зарегистрированных пользователей - очень высокие лимиты
                if "/api/math-generator" in path or "/api/ktp-generator" in path:
                    limit = 1000  # Практически без ограничений для генерации
                elif "/api/analytics" in path:
                    limit = 2000  # Высокий лимит для аналитики
                else:
                    limit = 1000  # Высокий лимит для остальных API
            else:
                # Для незарегистрированных пользователей - ограниченные лимиты
                if "/api/math-generator" in path or "/api/ktp-generator" in path:
                    limit = 3   # Ограничение: 3 генерации в минуту
                elif "/api/auth/login" in path or "/api/auth/register" in path:
                    limit = 10  # Лимит для попыток входа
                else:
                    limit = 30  # Лимит для остальных API
            
            # Создаем ключ для Redis
            redis_key = f"{ip}:{path}"
            
            # Пытаемся использовать Redis
            if redis_service.is_available():
                # Используем Redis для rate limiting
                redis_result = redis_service.increment_rate_limit(redis_key, window_minutes=1)
                
                if "error" in redis_result:
                    logger.warning(f"Redis error, falling back to memory: {redis_result['error']}")
                    return self._fallback_rate_limit(ip, path, is_authenticated, limit)
                
                current_requests = redis_result.get("total_requests", 0)
                
                if current_requests > limit:
                    # Получаем информацию о времени ожидания
                    info = redis_service.get_rate_limit_info(redis_key, window_minutes=1)
                    oldest_request_str = info.get("oldest_request")
                    
                    if oldest_request_str:
                        try:
                            oldest_request = datetime.fromisoformat(oldest_request_str)
                            next_available = oldest_request + timedelta(minutes=1)
                            now = datetime.utcnow()
                            seconds_to_wait = max(0, int((next_available - now).total_seconds()))
                        except:
                            seconds_to_wait = 60
                    else:
                        seconds_to_wait = 60
                    
                    return {
                        "allowed": False,
                        "current_requests": current_requests,
                        "limit": limit,
                        "seconds_to_wait": seconds_to_wait,
                        "is_authenticated": is_authenticated,
                        "retry_after": seconds_to_wait,
                        "storage": "redis"
                    }
                
                return {
                    "allowed": True,
                    "current_requests": current_requests,
                    "limit": limit,
                    "seconds_to_wait": 0,
                    "is_authenticated": is_authenticated,
                    "retry_after": 0,
                    "storage": "redis"
                }
            else:
                # Fallback к in-memory хранилищу
                logger.info("Redis недоступен, используем in-memory rate limiting")
                return self._fallback_rate_limit(ip, path, is_authenticated, limit)
            
        except Exception as e:
            logger.error(f"Ошибка в check_rate_limit_with_auth: {e}")
            # В случае ошибки разрешаем запрос
            return {
                "allowed": True,
                "current_requests": 0,
                "limit": 1000,
                "seconds_to_wait": 0,
                "is_authenticated": is_authenticated,
                "retry_after": 0,
                "error": str(e),
                "storage": "error"
            }
    
    def _fallback_rate_limit(self, ip: str, path: str, is_authenticated: bool, limit: int) -> dict:
        """Fallback к in-memory rate limiting"""
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=1)
            
            # Очищаем старые записи безопасно
            if ip in self.rate_limits:
                self.rate_limits[ip] = deque([
                    timestamp for timestamp in self.rate_limits[ip] 
                    if timestamp > window_start
                ])
            
            # Проверяем лимит
            current_requests = len(self.rate_limits[ip]) if ip in self.rate_limits else 0
            
            # Вычисляем время до следующего доступного запроса
            if current_requests >= limit:
                # Находим самый старый запрос в текущем окне
                if self.rate_limits[ip]:
                    oldest_request = min(self.rate_limits[ip])
                    next_available = oldest_request + timedelta(minutes=1)
                    seconds_to_wait = max(0, int((next_available - now).total_seconds()))
                else:
                    seconds_to_wait = 60
                
                return {
                    "allowed": False,
                    "current_requests": current_requests,
                    "limit": limit,
                    "seconds_to_wait": seconds_to_wait,
                    "is_authenticated": is_authenticated,
                    "retry_after": seconds_to_wait,
                    "storage": "memory"
                }
            
            # Добавляем текущий запрос
            if ip not in self.rate_limits:
                self.rate_limits[ip] = deque()
            self.rate_limits[ip].append(now)
            
            return {
                "allowed": True,
                "current_requests": current_requests + 1,
                "limit": limit,
                "seconds_to_wait": 0,
                "is_authenticated": is_authenticated,
                "retry_after": 0,
                "storage": "memory"
            }
            
        except Exception as e:
            logger.error(f"Ошибка в fallback rate limit: {e}")
            return {
                "allowed": True,
                "current_requests": 0,
                "limit": limit,
                "seconds_to_wait": 0,
                "is_authenticated": is_authenticated,
                "retry_after": 0,
                "error": str(e),
                "storage": "memory_error"
            }

    def check_rate_limit(self, ip: str, path: str) -> bool:
        """Безопасная проверка лимита запросов"""
        try:
            now = datetime.utcnow()
            window_start = now - timedelta(minutes=1)
            
            # Очищаем старые записи безопасно
            if ip in self.rate_limits:
                self.rate_limits[ip] = deque([
                    timestamp for timestamp in self.rate_limits[ip] 
                    if timestamp > window_start
                ])
            
            # Проверяем лимит
            current_requests = len(self.rate_limits[ip]) if ip in self.rate_limits else 0
            
            # Очень мягкие лимиты для разработки
            limit = 1000  # По умолчанию очень высокий лимит
            
            if "/api/auth/login" in path or "/api/auth/register" in path:
                limit = 100  # Мягкий лимит для аутентификации
            elif "/api/math-generator" in path or "/api/ktp-generator" in path:
                limit = 50   # Увеличенный лимит для генерации файлов
            elif "/api/admin" in path:
                limit = 200  # Очень высокий лимит для админ панели
            elif "/api/analytics" in path:
                limit = 500  # Очень высокий лимит для аналитики
            elif "/user" in path:
                limit = 200   # Высокий лимит для пользовательских данных
            
            if current_requests >= limit:
                # Блокируем IP на 15 минут при превышении
                self.blocked_ips[ip] = now + timedelta(minutes=15)
                return False
            
            # Добавляем текущий запрос
            self.rate_limits[ip].append(now)
            return True
        except Exception as e:
            logger.warning(f"Ошибка проверки rate limit для IP {ip}: {e}")
            return True  # В случае ошибки разрешаем запрос

    def is_ip_blocked(self, ip: str) -> bool:
        """Безопасная проверка заблокированных IP"""
        try:
            if ip in self.blocked_ips:
                if datetime.utcnow() > self.blocked_ips[ip]:
                    # Время блокировки истекло
                    del self.blocked_ips[ip]
                    return False
                return True
            return False
        except Exception as e:
            logger.warning(f"Ошибка проверки блокировки IP {ip}: {e}")
            return False  # В случае ошибки не блокируем

    def detect_malicious_patterns(self, text: str) -> bool:
        """Безопасное обнаружение вредоносных паттернов"""
        try:
            if not text or not isinstance(text, str):
                return False
                
            for pattern in self.compiled_patterns:
                if pattern.search(text):
                    return True
            return False
        except Exception as e:
            logger.warning(f"Ошибка поиска вредоносных паттернов: {e}")
            return False

    def is_valid_user_agent(self, user_agent: str) -> bool:
        """Безопасная проверка валидности User-Agent"""
        try:
            if not user_agent or not isinstance(user_agent, str) or len(user_agent) < 10:
                return False
            
            # Проверяем на подозрительные паттерны (исключаем нормальные браузеры)
            suspicious_agents = [
                'sqlmap', 'nikto', 'nmap', 'dirb', 'gobuster',
                'masscan', 'nessus', 'openvas', 'nuclei'
            ]
            
            user_agent_lower = user_agent.lower()
            for suspicious in suspicious_agents:
                if suspicious in user_agent_lower:
                    return False
            
            return True
        except Exception as e:
            logger.warning(f"Ошибка проверки User-Agent: {e}")
            return True  # В случае ошибки разрешаем

    def add_security_headers(self, response):
        """Безопасное добавление security headers"""
        try:
            if not response or not hasattr(response, 'headers'):
                return response
                
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            }
            
            # Добавляем CSP только если это не статические файлы
            if hasattr(response, 'media_type') and 'text/html' in str(response.media_type):
                security_headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline' fonts.googleapis.com; "
                    "font-src 'self' fonts.gstatic.com; "
                    "img-src 'self' data:; "
                    "connect-src 'self';"
                )
            
            for header, value in security_headers.items():
                try:
                    response.headers[header] = value
                except Exception as header_error:
                    logger.warning(f"Не удалось добавить заголовок {header}: {header_error}")
            
            return response
        except Exception as e:
            logger.warning(f"Ошибка добавления security headers: {e}")
            return response

    def create_rate_limit_response(self, rate_limit_result: dict, is_authenticated: bool):
        """Создание информативного ответа при превышении лимита"""
        try:
            seconds_to_wait = rate_limit_result.get("seconds_to_wait", 60)
            current_requests = rate_limit_result.get("current_requests", 0)
            limit = rate_limit_result.get("limit", 0)
            path = rate_limit_result.get("path", "")
            
            # Формируем сообщение в зависимости от типа пользователя
            if is_authenticated:
                message = f"Превышен лимит запросов ({current_requests}/{limit}). Попробуйте через {seconds_to_wait} секунд."
                suggestion = None
            else:
                if "/api/math-generator" in path or "/api/ktp-generator" in path:
                    message = f"Лимит генерации исчерпан ({current_requests}/{limit}). Следующая генерация доступна через {seconds_to_wait} секунд."
                    suggestion = "💡 Зарегистрируйтесь, чтобы убрать ограничения на генерацию!"
                else:
                    message = f"Превышен лимит запросов ({current_requests}/{limit}). Попробуйте через {seconds_to_wait} секунд."
                    suggestion = "💡 Зарегистрированные пользователи имеют больше возможностей."
            
            content = {
                "error": message,
                "code": "RATE_LIMIT_EXCEEDED",
                "details": {
                    "current_requests": current_requests,
                    "limit": limit,
                    "seconds_to_wait": seconds_to_wait,
                    "is_authenticated": is_authenticated,
                    "retry_after": seconds_to_wait
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if suggestion:
                content["suggestion"] = suggestion
                content["register_url"] = "/auth/register"
            
            response = JSONResponse(
                status_code=429,
                content=content,
                headers={
                    "Retry-After": str(seconds_to_wait),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(max(0, limit - current_requests)),
                    "X-RateLimit-Reset": str(int((datetime.utcnow() + timedelta(seconds=seconds_to_wait)).timestamp())),
                    # Добавляем CORS заголовки
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Credentials": "true"
                }
            )
            return response
        except Exception as e:
            logger.error(f"Ошибка создания rate limit response: {e}")
            return self.create_security_response("Превышен лимит запросов", 429)

    def create_security_response(self, message: str, status_code: int):
        """Безопасное создание ответа для блокировки"""
        try:
            response = JSONResponse(
                status_code=status_code,
                content={
                    "error": message,
                    "code": "SECURITY_VIOLATION",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            # Добавляем CORS заголовки для совместимости
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        except Exception as e:
            logger.error(f"Ошибка создания security response: {e}")
            # Возвращаем минимальный ответ
            response = JSONResponse(
                status_code=500,
                content={"error": "Security error"}
            )
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

    def log_security_event(self, ip: str, event_type: str, details: str):
        """Безопасное логирование событий безопасности"""
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "ip": str(ip) if ip else "unknown",
                "type": str(event_type) if event_type else "unknown",
                "details": str(details)[:500] if details else ""  # Ограничиваем длину
            }
            
            self.security_log.append(event)
            logger.warning(f"SECURITY: {event_type} from {ip}: {str(details)[:100]}...")
        except Exception as e:
            logger.error(f"Ошибка логирования события безопасности: {e}")

    def log_request(self, ip: str, request: Request, response, processing_time: float):
        """Безопасное логирование обычных запросов"""
        try:
            if settings.debug and hasattr(request, 'method') and hasattr(request, 'url'):
                logger.info(
                    f"{request.method} {request.url.path} - "
                    f"IP: {ip} - "
                    f"Status: {getattr(response, 'status_code', 'unknown')} - "
                    f"Time: {processing_time:.3f}s"
                )
        except Exception as e:
            logger.warning(f"Ошибка логирования запроса: {e}")

    def get_security_stats(self) -> Dict:
        """Безопасное получение статистики безопасности"""
        try:
            now = datetime.utcnow()
            last_hour = now - timedelta(hours=1)
            
            recent_events = []
            for event in self.security_log:
                try:
                    if datetime.fromisoformat(event["timestamp"]) > last_hour:
                        recent_events.append(event)
                except (KeyError, ValueError):
                    continue
            
            event_counts = defaultdict(int)
            for event in recent_events:
                try:
                    event_counts[event.get("type", "unknown")] += 1
                except Exception:
                    continue
            
            return {
                "blocked_ips_count": len(self.blocked_ips),
                "active_rate_limits": len(self.rate_limits),
                "recent_security_events": len(recent_events),
                "event_types": dict(event_counts),
                "total_security_logs": len(self.security_log)
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики безопасности: {e}")
            return {
                "blocked_ips_count": 0,
                "active_rate_limits": 0,
                "recent_security_events": 0,
                "event_types": {},
                "total_security_logs": 0,
                "error": str(e)
            }

class CSRFProtection:
    """CSRF защита для форм"""
    
    def __init__(self):
        self.tokens: Set[str] = set()
    
    def generate_token(self) -> str:
        """Генерация CSRF токена"""
        try:
            token = secrets.token_urlsafe(32)
            self.tokens.add(token)
            return token
        except Exception as e:
            logger.error(f"Ошибка генерации CSRF токена: {e}")
            return secrets.token_hex(16)  # Fallback
    
    def validate_token(self, token: str) -> bool:
        """Валидация CSRF токена"""
        try:
            if token in self.tokens:
                self.tokens.remove(token)  # Токен одноразовый
                return True
            return False
        except Exception as e:
            logger.error(f"Ошибка валидации CSRF токена: {e}")
            return False
    
    def cleanup_expired_tokens(self):
        """Очистка устаревших токенов"""
        try:
            # В реальном проекте токены должны иметь TTL
            if len(self.tokens) > 1000:
                self.tokens.clear()
        except Exception as e:
            logger.error(f"Ошибка очистки CSRF токенов: {e}")

# Глобальный экземпляр CSRF защиты
csrf_protection = CSRFProtection() 