from fastapi import Request, Response
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import json
from typing import Union

from app.services.i18n_service import i18n_service, SupportedLanguage

class I18nMiddleware(BaseHTTPMiddleware):
    """Middleware для интернационализации"""
    
    def __init__(self, app):
        super().__init__(app)
        self.i18n = i18n_service

    async def dispatch(self, request: Request, call_next):
        """Основная логика middleware"""
        
        # Определяем язык пользователя
        user_language = self.detect_user_language(request)
        
        # Сохраняем язык в state запроса
        request.state.language = user_language
        
        # Выполняем запрос
        response = await call_next(request)
        
        # Переводим ответ если это JSON API (но НЕ файловые загрузки)
        if (
            hasattr(response, 'media_type') and 
            response.media_type == 'application/json' and
            request.url.path.startswith('/api/') and
            not isinstance(response, FileResponse)
        ):
            response = await self.translate_json_response(response, user_language)
        
        # Добавляем заголовок с языком
        response.headers['Content-Language'] = user_language
        
        return response

    def detect_user_language(self, request: Request) -> str:
        """Определение языка пользователя"""
        
        # 1. Проверяем query параметр ?lang=
        lang_param = request.query_params.get('lang')
        if lang_param and lang_param in [lang.value for lang in SupportedLanguage]:
            return lang_param
        
        # 2. Проверяем заголовок X-Language
        lang_header = request.headers.get('X-Language')
        if lang_header and lang_header in [lang.value for lang in SupportedLanguage]:
            return lang_header
        
        # 3. Проверяем cookie
        lang_cookie = request.cookies.get('language')
        if lang_cookie and lang_cookie in [lang.value for lang in SupportedLanguage]:
            return lang_cookie
        
        # 4. Определяем по заголовку Accept-Language
        accept_language = request.headers.get('Accept-Language', '')
        detected_lang = self.i18n.detect_language_from_accept_header(accept_language)
        
        return detected_lang

    async def translate_json_response(self, response: Response, language: str) -> Response:
        """Перевод JSON ответа"""
        try:
            # Читаем тело ответа
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Парсим JSON
            if body:
                try:
                    data = json.loads(body.decode())
                    
                    # Переводим данные
                    translated_data = self.i18n.translate_response_data(data, language)
                    
                    # Создаем новый ответ с переведенными данными
                    return JSONResponse(
                        content=translated_data,
                        status_code=response.status_code,
                        headers=dict(response.headers)
                    )
                except json.JSONDecodeError:
                    # Если не JSON, возвращаем как есть
                    pass
            
            # Если что-то пошло не так, возвращаем оригинальный ответ
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
            
        except Exception as e:
            # Логируем ошибку но не ломаем ответ
            print(f"I18n middleware error: {e}")
            return response

def get_user_language(request: Request) -> str:
    """Получение языка пользователя из request state"""
    return getattr(request.state, 'language', SupportedLanguage.RUSSIAN) 