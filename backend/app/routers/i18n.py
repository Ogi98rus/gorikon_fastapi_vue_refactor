from fastapi import APIRouter, Request, Response, Depends, Query
from typing import Optional, Dict, List
from pydantic import BaseModel

from app.services.i18n_service import i18n_service, SupportedLanguage
from app.middleware.i18n import get_user_language

router = APIRouter(prefix="/api/i18n", tags=["Интернационализация"])

@router.get("/languages")
async def get_supported_languages():
    """Получение списка поддерживаемых языков"""
    return {
        "supported_languages": i18n_service.get_supported_languages(),
        "default_language": i18n_service.default_language,
        "fallback_language": i18n_service.fallback_language
    }

@router.get("/translations")
async def get_translations(
    request: Request,
    language: Optional[str] = Query(None, description="Код языка (ru, en, kk, be, uk)")
):
    """Получение всех переводов для языка"""
    
    # Используем переданный язык или определяем автоматически
    if not language:
        language = get_user_language(request)
    
    # Проверяем поддерживается ли язык
    if language not in [lang.value for lang in SupportedLanguage]:
        language = i18n_service.default_language
    
    translations = i18n_service.get_translations_for_language(language)
    
    return {
        "language": language,
        "translations": translations,
        "total_keys": len(translations)
    }

@router.get("/translations/{language}")
async def get_translations_by_language(
    language: str
):
    """Получение всех переводов для определенного языка"""
    
    # Проверяем поддерживается ли язык
    if language not in [lang.value for lang in SupportedLanguage]:
        language = i18n_service.default_language
    
    translations = i18n_service.get_translations_for_language(language)
    
    return {
        "language": language,
        "translations": translations,
        "total_keys": len(translations)
    }

@router.get("/translate/{key}")
async def get_translation(
    key: str,
    request: Request,
    language: Optional[str] = Query(None, description="Код языка")
):
    """Получение перевода по ключу"""
    
    if not language:
        language = get_user_language(request)
    
    translation = i18n_service.get_translation(key, language)
    
    return {
        "key": key,
        "language": language,
        "translation": translation,
        "found": translation != key
    }

from pydantic import BaseModel

class SetLanguageRequest(BaseModel):
    language: str
    permanent: bool = False

@router.post("/set-language")
async def set_language(
    language_req: SetLanguageRequest,
    response: Response
):
    """Установка языка пользователя"""
    
    # Проверяем поддерживается ли язык
    if language_req.language not in [lang.value for lang in SupportedLanguage]:
        return {
            "error": "Неподдерживаемый язык",
            "supported_languages": [lang.value for lang in SupportedLanguage]
        }
    
    # Устанавливаем cookie если нужно
    if language_req.permanent:
        response.set_cookie(
            key="language",
            value=language_req.language,
            max_age=365*24*60*60,  # 1 год
            httponly=True,
            secure=True,
            samesite="lax"
        )
    
    return {
        "message": "Язык установлен",
        "language": language_req.language,
        "permanent": language_req.permanent,
        "language_name": next(
            (lang["native_name"] for lang in i18n_service.get_supported_languages() 
             if lang["code"] == language_req.language), 
            language_req.language
        )
    }

@router.get("/detect")
async def detect_language(request: Request):
    """Определение языка пользователя"""
    
    detected_language = get_user_language(request)
    accept_language = request.headers.get('Accept-Language', '')
    
    # Получаем информацию о том, как был определен язык
    detection_method = "default"
    
    if request.query_params.get('lang'):
        detection_method = "query_parameter"
    elif request.headers.get('X-Language'):
        detection_method = "header"
    elif request.cookies.get('language'):
        detection_method = "cookie"
    elif accept_language:
        detection_method = "accept_language"
    
    return {
        "detected_language": detected_language,
        "detection_method": detection_method,
        "accept_language_header": accept_language,
        "language_info": next(
            (lang for lang in i18n_service.get_supported_languages() 
             if lang["code"] == detected_language), 
            None
        )
    }

@router.get("/demo")
async def translation_demo(
    request: Request,
    keys: List[str] = Query(
        default=["welcome", "error", "success", "nav.home", "auth.login"],
        description="Ключи для демонстрации перевода"
    )
):
    """Демонстрация переводов для разных языков"""
    
    demo_translations = {}
    
    for language_info in i18n_service.get_supported_languages():
        language_code = language_info["code"]
        demo_translations[language_code] = {
            "language_info": language_info,
            "translations": {}
        }
        
        for key in keys:
            translation = i18n_service.get_translation(key, language_code)
            demo_translations[language_code]["translations"][key] = translation
    
    current_language = get_user_language(request)
    
    return {
        "current_language": current_language,
        "demo_keys": keys,
        "translations_by_language": demo_translations
    }

@router.get("/stats")
async def get_translation_stats():
    """Статистика переводов"""
    
    stats = {}
    total_keys = 0
    
    for language_info in i18n_service.get_supported_languages():
        language_code = language_info["code"]
        translations = i18n_service.get_translations_for_language(language_code)
        key_count = len(translations)
        
        stats[language_code] = {
            "language_info": language_info,
            "total_keys": key_count,
            "coverage_percentage": 100.0  # Пока считаем что все языки покрыты полностью
        }
        
        if key_count > total_keys:
            total_keys = key_count
    
    # Пересчитываем процент покрытия относительно самого полного языка
    for language_code in stats:
        current_keys = stats[language_code]["total_keys"]
        stats[language_code]["coverage_percentage"] = round(
            (current_keys / total_keys) * 100, 1
        ) if total_keys > 0 else 0
    
    return {
        "total_translation_keys": total_keys,
        "supported_languages_count": len(stats),
        "languages_stats": stats
    }

@router.get("/missing-translations")
async def get_missing_translations():
    """Получение недостающих переводов"""
    
    # Находим язык с максимальным количеством ключей (обычно русский)
    max_keys = 0
    reference_language = None
    reference_keys = set()
    
    for language_info in i18n_service.get_supported_languages():
        language_code = language_info["code"]
        translations = i18n_service.get_translations_for_language(language_code)
        
        if len(translations) > max_keys:
            max_keys = len(translations)
            reference_language = language_code
            reference_keys = set(translations.keys())
    
    # Проверяем недостающие ключи для каждого языка
    missing_translations = {}
    
    for language_info in i18n_service.get_supported_languages():
        language_code = language_info["code"]
        
        if language_code == reference_language:
            continue
        
        translations = i18n_service.get_translations_for_language(language_code)
        current_keys = set(translations.keys())
        
        missing_keys = reference_keys - current_keys
        
        if missing_keys:
            missing_translations[language_code] = {
                "language_info": language_info,
                "missing_keys": sorted(list(missing_keys)),
                "missing_count": len(missing_keys),
                "total_keys": len(current_keys),
                "completion_percentage": round(
                    (len(current_keys) / len(reference_keys)) * 100, 1
                )
            }
    
    return {
        "reference_language": reference_language,
        "reference_keys_count": len(reference_keys),
        "languages_with_missing_translations": missing_translations,
        "total_languages_incomplete": len(missing_translations)
    } 