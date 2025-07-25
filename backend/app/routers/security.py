from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List

from app.models.database import get_db, User
from app.dependencies.auth import get_current_superuser
from app.middleware.security import csrf_protection

router = APIRouter(prefix="/api/security", tags=["Безопасность"])

# Получаем экземпляр SecurityMiddleware (будет внедрен в main.py)
security_middleware = None

def set_security_middleware(middleware):
    """Устанавливает ссылку на SecurityMiddleware"""
    global security_middleware
    security_middleware = middleware

@router.get("/stats")
async def get_security_stats(
    current_user: User = Depends(get_current_superuser)
):
    """Получение статистики безопасности (только для суперпользователей)"""
    if not security_middleware:
        raise HTTPException(status_code=503, detail="Security middleware не инициализирован")
    
    try:
        stats = security_middleware.get_security_stats()
        
        return {
            "security_stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
            "middleware_status": "active"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения статистики: {str(e)}")

@router.get("/events")
async def get_security_events(
    limit: int = 50,
    event_type: str = None,
    current_user: User = Depends(get_current_superuser)
):
    """Получение логов событий безопасности"""
    if not security_middleware:
        raise HTTPException(status_code=503, detail="Security middleware не инициализирован")
    
    try:
        # Получаем последние события
        events = list(security_middleware.security_log)
        
        # Фильтруем по типу если указан
        if event_type:
            events = [event for event in events if event["type"] == event_type]
        
        # Ограничиваем количество
        events = events[-limit:] if len(events) > limit else events
        
        # Сортируем по времени (последние первыми)
        events.reverse()
        
        return {
            "events": events,
            "total_count": len(events),
            "available_types": list(set([event["type"] for event in security_middleware.security_log]))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения событий: {str(e)}")

@router.get("/blocked-ips")
async def get_blocked_ips(
    current_user: User = Depends(get_current_superuser)
):
    """Получение списка заблокированных IP адресов"""
    if not security_middleware:
        raise HTTPException(status_code=503, detail="Security middleware не инициализирован")
    
    try:
        now = datetime.utcnow()
        blocked_ips = []
        
        for ip, block_until in security_middleware.blocked_ips.items():
            blocked_ips.append({
                "ip": ip,
                "blocked_until": block_until.isoformat(),
                "remaining_minutes": max(0, int((block_until - now).total_seconds() / 60))
            })
        
        return {
            "blocked_ips": blocked_ips,
            "total_blocked": len(blocked_ips)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения заблокированных IP: {str(e)}")

@router.post("/unblock-ip")
async def unblock_ip(
    ip_address: str,
    current_user: User = Depends(get_current_superuser)
):
    """Разблокировка IP адреса"""
    if not security_middleware:
        raise HTTPException(status_code=503, detail="Security middleware не инициализирован")
    
    try:
        if ip_address in security_middleware.blocked_ips:
            del security_middleware.blocked_ips[ip_address]
            
            # Логируем событие
            security_middleware.log_security_event(
                current_user.email, 
                "IP_UNBLOCKED", 
                f"Admin unblocked IP: {ip_address}"
            )
            
            return {
                "message": f"IP адрес {ip_address} разблокирован",
                "unblocked_by": current_user.email
            }
        else:
            raise HTTPException(status_code=404, detail="IP адрес не найден в списке заблокированных")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка разблокировки IP: {str(e)}")

@router.post("/block-ip")
async def block_ip(
    ip_address: str,
    duration_minutes: int = 60,
    reason: str = "Manual block",
    current_user: User = Depends(get_current_superuser)
):
    """Ручная блокировка IP адреса"""
    if not security_middleware:
        raise HTTPException(status_code=503, detail="Security middleware не инициализирован")
    
    try:
        # Валидация параметров
        if duration_minutes < 1 or duration_minutes > 1440:  # Максимум 24 часа
            raise HTTPException(status_code=400, detail="Длительность блокировки должна быть от 1 до 1440 минут")
        
        # Блокируем IP
        block_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        security_middleware.blocked_ips[ip_address] = block_until
        
        # Логируем событие
        security_middleware.log_security_event(
            current_user.email,
            "IP_BLOCKED_MANUAL",
            f"Admin blocked IP: {ip_address} for {duration_minutes}min. Reason: {reason}"
        )
        
        return {
            "message": f"IP адрес {ip_address} заблокирован на {duration_minutes} минут",
            "blocked_until": block_until.isoformat(),
            "reason": reason,
            "blocked_by": current_user.email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка блокировки IP: {str(e)}")

@router.get("/csrf-token")
async def get_csrf_token():
    """Получение CSRF токена для форм"""
    try:
        token = csrf_protection.generate_token()
        return {
            "csrf_token": token,
            "expires_in": 3600  # 1 час
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации CSRF токена: {str(e)}")

@router.post("/validate-csrf")
async def validate_csrf_token(
    csrf_token: str
):
    """Валидация CSRF токена"""
    try:
        is_valid = csrf_protection.validate_token(csrf_token)
        return {
            "valid": is_valid,
            "message": "Токен валиден" if is_valid else "Недействительный токен"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка валидации CSRF токена: {str(e)}")

@router.post("/clear-security-logs")
async def clear_security_logs(
    current_user: User = Depends(get_current_superuser)
):
    """Очистка логов безопасности"""
    if not security_middleware:
        raise HTTPException(status_code=503, detail="Security middleware не инициализирован")
    
    try:
        logs_count = len(security_middleware.security_log)
        security_middleware.security_log.clear()
        
        # Логируем очистку
        security_middleware.log_security_event(
            current_user.email,
            "LOGS_CLEARED",
            f"Admin cleared {logs_count} security log entries"
        )
        
        return {
            "message": f"Очищено {logs_count} записей в логах безопасности",
            "cleared_by": current_user.email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка очистки логов: {str(e)}")

@router.get("/rate-limits")
async def get_rate_limits_info(
    current_user: User = Depends(get_current_superuser)
):
    """Получение информации о rate limiting"""
    if not security_middleware:
        raise HTTPException(status_code=503, detail="Security middleware не инициализирован")
    
    try:
        rate_limits_info = []
        now = datetime.utcnow()
        
        for ip, timestamps in security_middleware.rate_limits.items():
            recent_requests = len([t for t in timestamps if (now - t).total_seconds() < 60])
            
            if recent_requests > 0:
                rate_limits_info.append({
                    "ip": ip,
                    "requests_last_minute": recent_requests,
                    "last_request": max(timestamps).isoformat() if timestamps else None
                })
        
        return {
            "rate_limits": rate_limits_info,
            "total_tracked_ips": len(rate_limits_info)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения rate limits: {str(e)}")

@router.get("/rate-limit-status")
async def get_rate_limit_status(
    request: Request
):
    """Проверка статуса rate limit для текущего пользователя (доступно всем)"""
    try:
        # Определяем аутентификацию пользователя
        is_authenticated = False
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer ") or request.cookies.get("access_token"):
            is_authenticated = True
        
        if not security_middleware:
            return {
                "authenticated": is_authenticated,
                "unlimited": is_authenticated,
                "limits": {
                    "ktp_generator": {"allowed": True, "unlimited": is_authenticated},
                    "math_generator": {"allowed": True, "unlimited": is_authenticated}
                }
            }
        
        # Получаем IP пользователя
        client_ip = security_middleware.get_client_ip(request)
        
        # Проверяем статус для генераторов (НЕ добавляем запрос, только проверяем)
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=1)
        
        # Считаем текущие запросы
        current_requests = 0
        if client_ip in security_middleware.rate_limits:
            current_requests = len([
                t for t in security_middleware.rate_limits[client_ip] 
                if t > window_start
            ])
        
        # Определяем лимиты
        if is_authenticated:
            ktp_limit = math_limit = 1000  # Практически без ограничений
        else:
            ktp_limit = math_limit = 3  # 3 генерации в минуту
        
        # Вычисляем время ожидания
        seconds_to_wait = 0
        if current_requests >= ktp_limit and client_ip in security_middleware.rate_limits:
            oldest_request = min(security_middleware.rate_limits[client_ip])
            next_available = oldest_request + timedelta(minutes=1)
            seconds_to_wait = max(0, int((next_available - now).total_seconds()))
        
        return {
            "authenticated": is_authenticated,
            "unlimited": is_authenticated,
            "limits": {
                "ktp_generator": {
                    "allowed": current_requests < ktp_limit,
                    "current_requests": current_requests,
                    "limit": ktp_limit,
                    "seconds_to_wait": seconds_to_wait,
                    "unlimited": is_authenticated
                },
                "math_generator": {
                    "allowed": current_requests < math_limit,
                    "current_requests": current_requests,
                    "limit": math_limit,
                    "seconds_to_wait": seconds_to_wait,
                    "unlimited": is_authenticated
                }
            }
        }
        
    except Exception as e:
        return {
            "authenticated": False,
            "unlimited": False,
            "error": str(e),
            "limits": {
                "ktp_generator": {"allowed": True, "unlimited": False},
                "math_generator": {"allowed": True, "unlimited": False}
            }
        }

@router.get("/health")
async def security_health_check():
    """Проверка состояния системы безопасности"""
    try:
        status = {
            "security_middleware": security_middleware is not None,
            "csrf_protection": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if security_middleware:
            stats = security_middleware.get_security_stats()
            status.update({
                "blocked_ips": stats["blocked_ips_count"],
                "active_rate_limits": stats["active_rate_limits"],
                "security_events_count": stats["total_security_logs"]
            })
        
        return {
            "status": "healthy" if status["security_middleware"] else "degraded",
            "components": status
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 