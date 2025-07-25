from typing import Dict, Optional, List
import json
import os
from pathlib import Path
from enum import Enum

class SupportedLanguage(str, Enum):
    """Поддерживаемые языки"""
    RUSSIAN = "ru"
    ENGLISH = "en"
    KAZAKH = "kk"
    BELARUSIAN = "be"
    UKRAINIAN = "uk"

class I18nService:
    """Сервис интернационализации"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_language = SupportedLanguage.RUSSIAN
        self.fallback_language = SupportedLanguage.ENGLISH
        
        # Загружаем переводы
        self.load_translations()
    
    def load_translations(self):
        """Загрузка переводов из файлов"""
        # Словари переводов встроены в код для простоты
        self.translations = {
            SupportedLanguage.RUSSIAN: {
                # Общие
                "app.name": "Генератор учебных материалов",
                "app.description": "Генератор математических примеров и календарно-тематического планирования",
                "app.version": "Версия",
                "welcome": "Добро пожаловать",
                "error": "Ошибка",
                "success": "Успешно",
                "loading": "Загрузка...",
                "submit": "Отправить",
                "cancel": "Отмена",
                "save": "Сохранить",
                "delete": "Удалить",
                "edit": "Редактировать",
                "close": "Закрыть",
                "back": "Назад",
                "next": "Далее",
                "previous": "Предыдущий",
                "confirm": "Подтвердить",
                "required": "Обязательное поле",
                "optional": "Необязательное",
                
                # Навигация
                "nav.home": "Главная",
                "nav.math_generator": "Математический генератор",
                "nav.ktp_generator": "КТП генератор",
                "nav.analytics": "Аналитика",
                "nav.auth": "Вход",
                "nav.profile": "Профиль",
                "nav.logout": "Выход",
                
                # Аутентификация
                "auth.login": "Вход в систему",
                "auth.register": "Регистрация",
                "auth.email": "Электронная почта",
                "auth.password": "Пароль",
                "auth.full_name": "Полное имя",
                "auth.school_name": "Название школы",
                "auth.login_success": "Вход выполнен успешно",
                "auth.register_success": "Регистрация завершена",
                "auth.logout_success": "Выход выполнен",
                "auth.invalid_credentials": "Неверные учетные данные",
                "auth.user_exists": "Пользователь уже существует",
                "auth.token_expired": "Токен истек",
                "auth.unauthorized": "Необходима авторизация",
                "auth.forbidden": "Доступ запрещен",
                
                # Математический генератор
                "math.title": "Генератор математических примеров",
                "math.num_operands": "Количество операндов",
                "math.operations": "Операции",
                "math.interval_start": "Начало диапазона",
                "math.interval_end": "Конец диапазона",
                "math.example_count": "Количество примеров",
                "math.operation.add": "Сложение (+)",
                "math.operation.subtract": "Вычитание (-)",
                "math.operation.multiply": "Умножение (*)",
                "math.operation.divide": "Деление (/)",
                "math.generate": "Создать примеры",
                "math.generated": "Примеры созданы",
                "math.download": "Скачать PDF",
                
                # КТП генератор
                "ktp.title": "Генератор календарно-тематического планирования",
                "ktp.start_date": "Дата начала",
                "ktp.end_date": "Дата окончания",
                "ktp.weekdays": "Рабочие дни",
                "ktp.lessons_per_day": "Уроков в день",
                "ktp.holidays": "Праздники",
                "ktp.vacation": "Каникулы",
                "ktp.file_name": "Имя файла",
                "ktp.monday": "Понедельник",
                "ktp.tuesday": "Вторник",
                "ktp.wednesday": "Среда",
                "ktp.thursday": "Четверг",
                "ktp.friday": "Пятница",
                "ktp.saturday": "Суббота",
                "ktp.sunday": "Воскресенье",
                "ktp.generate": "Создать планирование",
                "ktp.generated": "Планирование создано",
                "ktp.download": "Скачать Excel",
                
                # Аналитика
                "analytics.title": "Аналитика и статистика",
                "analytics.dashboard": "Дашборд",
                "analytics.total_generations": "Всего генераций",
                "analytics.math_generations": "Математических",
                "analytics.ktp_generations": "КТП",
                "analytics.popular_operations": "Популярные операции",
                "analytics.user_stats": "Личная статистика",
                "analytics.public_stats": "Общая статистика",
                "analytics.recent_activity": "Недавняя активность",
                "analytics.export": "Экспорт данных",
                
                # Безопасность
                "security.title": "Система безопасности",
                "security.blocked_ips": "Заблокированные IP",
                "security.security_events": "События безопасности",
                "security.rate_limits": "Ограничения запросов",
                "security.csrf_token": "CSRF токен",
                "security.unblock_ip": "Разблокировать IP",
                "security.block_ip": "Заблокировать IP",
                "security.clear_logs": "Очистить логи",
                
                # Ошибки
                "error.general": "Произошла ошибка",
                "error.validation": "Ошибка валидации",
                "error.network": "Ошибка сети",
                "error.server": "Ошибка сервера",
                "error.not_found": "Не найдено",
                "error.rate_limit": "Превышен лимит запросов",
                "error.file_too_large": "Файл слишком большой",
                "error.invalid_format": "Неверный формат",
                
                # Уведомления
                "notification.offline": "Нет подключения к интернету",
                "notification.online": "Подключение восстановлено",
                "notification.app_updated": "Приложение обновлено",
                "notification.install_app": "Установить приложение",
                "notification.app_installed": "Приложение установлено",
            },
            
            SupportedLanguage.ENGLISH: {
                # General
                "app.name": "Educational Materials Generator",
                "app.description": "Generator for math problems and curriculum planning",
                "app.version": "Version",
                "welcome": "Welcome",
                "error": "Error",
                "success": "Success",
                "loading": "Loading...",
                "submit": "Submit",
                "cancel": "Cancel",
                "save": "Save",
                "delete": "Delete",
                "edit": "Edit",
                "close": "Close",
                "back": "Back",
                "next": "Next",
                "previous": "Previous",
                "confirm": "Confirm",
                "required": "Required field",
                "optional": "Optional",
                
                # Navigation
                "nav.home": "Home",
                "nav.math_generator": "Math Generator",
                "nav.ktp_generator": "Curriculum Generator",
                "nav.analytics": "Analytics",
                "nav.auth": "Login",
                "nav.profile": "Profile",
                "nav.logout": "Logout",
                
                # Authentication
                "auth.login": "Login",
                "auth.register": "Register",
                "auth.email": "Email",
                "auth.password": "Password",
                "auth.full_name": "Full Name",
                "auth.school_name": "School Name",
                "auth.login_success": "Login successful",
                "auth.register_success": "Registration completed",
                "auth.logout_success": "Logout successful",
                "auth.invalid_credentials": "Invalid credentials",
                "auth.user_exists": "User already exists",
                "auth.token_expired": "Token expired",
                "auth.unauthorized": "Authorization required",
                "auth.forbidden": "Access denied",
                
                # Math Generator
                "math.title": "Math Problems Generator",
                "math.num_operands": "Number of operands",
                "math.operations": "Operations",
                "math.interval_start": "Range start",
                "math.interval_end": "Range end",
                "math.example_count": "Number of examples",
                "math.operation.add": "Addition (+)",
                "math.operation.subtract": "Subtraction (-)",
                "math.operation.multiply": "Multiplication (*)",
                "math.operation.divide": "Division (/)",
                "math.generate": "Generate Examples",
                "math.generated": "Examples generated",
                "math.download": "Download PDF",
                
                # KTP Generator
                "ktp.title": "Curriculum Planning Generator",
                "ktp.start_date": "Start date",
                "ktp.end_date": "End date",
                "ktp.weekdays": "Working days",
                "ktp.lessons_per_day": "Lessons per day",
                "ktp.holidays": "Holidays",
                "ktp.vacation": "Vacations",
                "ktp.file_name": "File name",
                "ktp.monday": "Monday",
                "ktp.tuesday": "Tuesday",
                "ktp.wednesday": "Wednesday",
                "ktp.thursday": "Thursday",
                "ktp.friday": "Friday",
                "ktp.saturday": "Saturday",
                "ktp.sunday": "Sunday",
                "ktp.generate": "Generate Planning",
                "ktp.generated": "Planning generated",
                "ktp.download": "Download Excel",
                
                # Analytics
                "analytics.title": "Analytics and Statistics",
                "analytics.dashboard": "Dashboard",
                "analytics.total_generations": "Total generations",
                "analytics.math_generations": "Math generations",
                "analytics.ktp_generations": "Curriculum generations",
                "analytics.popular_operations": "Popular operations",
                "analytics.user_stats": "Personal statistics",
                "analytics.public_stats": "Public statistics",
                "analytics.recent_activity": "Recent activity",
                "analytics.export": "Export data",
                
                # Security
                "security.title": "Security System",
                "security.blocked_ips": "Blocked IPs",
                "security.security_events": "Security events",
                "security.rate_limits": "Rate limits",
                "security.csrf_token": "CSRF token",
                "security.unblock_ip": "Unblock IP",
                "security.block_ip": "Block IP",
                "security.clear_logs": "Clear logs",
                
                # Errors
                "error.general": "An error occurred",
                "error.validation": "Validation error",
                "error.network": "Network error",
                "error.server": "Server error",
                "error.not_found": "Not found",
                "error.rate_limit": "Rate limit exceeded",
                "error.file_too_large": "File too large",
                "error.invalid_format": "Invalid format",
                
                # Notifications
                "notification.offline": "No internet connection",
                "notification.online": "Connection restored",
                "notification.app_updated": "App updated",
                "notification.install_app": "Install app",
                "notification.app_installed": "App installed",
            },
            
            # Добавим основные переводы для других языков
            SupportedLanguage.KAZAKH: {
                "app.name": "Оқу материалдарының генераторы",
                "welcome": "Қош келдіңіз",
                "error": "Қате",
                "success": "Сәтті",
                "nav.home": "Басты бет",
                "nav.math_generator": "Математика генераторы",
                "nav.ktp_generator": "КТЖ генераторы",
                "auth.login": "Кіру",
                "auth.register": "Тіркелу",
                "auth.email": "Электрондық пошта",
                "auth.password": "Құпия сөз",
            },
            
            SupportedLanguage.BELARUSIAN: {
                "app.name": "Генератар навучальных матэрыялаў",
                "welcome": "Сардэчна запрашаем",
                "error": "Памылка",
                "success": "Паспяхова",
                "nav.home": "Галоўная",
                "nav.math_generator": "Матэматычны генератар",
                "nav.ktp_generator": "КТП генератар",
                "auth.login": "Увайсці",
                "auth.register": "Рэгістрацыя",
                "auth.email": "Электронная пошта",
                "auth.password": "Пароль",
            },
            
            SupportedLanguage.UKRAINIAN: {
                "app.name": "Генератор навчальних матеріалів",
                "welcome": "Ласкаво просимо",
                "error": "Помилка",
                "success": "Успішно",
                "nav.home": "Головна",
                "nav.math_generator": "Математичний генератор",
                "nav.ktp_generator": "КТП генератор",
                "auth.login": "Увійти",
                "auth.register": "Реєстрація",
                "auth.email": "Електронна пошта",
                "auth.password": "Пароль",
            }
        }
    
    def get_translation(self, key: str, language: str = None, **kwargs) -> str:
        """Получение перевода по ключу"""
        if not language:
            language = self.default_language
        
        # Проверяем поддерживается ли язык
        if language not in self.translations:
            language = self.fallback_language
        
        # Получаем перевод
        translation = self.translations[language].get(key)
        
        # Если перевода нет, пробуем fallback язык
        if not translation and language != self.fallback_language:
            translation = self.translations[self.fallback_language].get(key)
        
        # Если всё ещё нет перевода, возвращаем ключ
        if not translation:
            translation = key
        
        # Форматируем строку если есть параметры
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except (KeyError, ValueError):
                pass  # Игнорируем ошибки форматирования
        
        return translation
    
    def get_translations_for_language(self, language: str) -> Dict[str, str]:
        """Получение всех переводов для языка"""
        if language not in self.translations:
            language = self.fallback_language
        
        return self.translations[language].copy()
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Получение списка поддерживаемых языков"""
        return [
            {
                "code": SupportedLanguage.RUSSIAN,
                "name": "Русский",
                "native_name": "Русский"
            },
            {
                "code": SupportedLanguage.ENGLISH,
                "name": "English",
                "native_name": "English"
            },
            {
                "code": SupportedLanguage.KAZAKH,
                "name": "Kazakh",
                "native_name": "Қазақша"
            },
            {
                "code": SupportedLanguage.BELARUSIAN,
                "name": "Belarusian",
                "native_name": "Беларуская"
            },
            {
                "code": SupportedLanguage.UKRAINIAN,
                "name": "Ukrainian",
                "native_name": "Українська"
            }
        ]
    
    def detect_language_from_accept_header(self, accept_language: str) -> str:
        """Определение языка из заголовка Accept-Language"""
        if not accept_language:
            return self.default_language
        
        # Парсим заголовок Accept-Language
        languages = []
        for lang_range in accept_language.split(','):
            lang_range = lang_range.strip()
            if ';' in lang_range:
                lang, weight = lang_range.split(';', 1)
                try:
                    weight = float(weight.split('=')[1])
                except (ValueError, IndexError):
                    weight = 1.0
            else:
                lang, weight = lang_range, 1.0
            
            lang = lang.strip().lower()
            
            # Приводим к нашим кодам языков
            if lang.startswith('ru'):
                lang = SupportedLanguage.RUSSIAN
            elif lang.startswith('en'):
                lang = SupportedLanguage.ENGLISH
            elif lang.startswith('kk'):
                lang = SupportedLanguage.KAZAKH
            elif lang.startswith('be'):
                lang = SupportedLanguage.BELARUSIAN
            elif lang.startswith('uk'):
                lang = SupportedLanguage.UKRAINIAN
            else:
                continue  # Неподдерживаемый язык
            
            languages.append((lang, weight))
        
        # Сортируем по весу
        languages.sort(key=lambda x: x[1], reverse=True)
        
        # Возвращаем первый поддерживаемый язык
        for lang, _ in languages:
            if lang in self.translations:
                return lang
        
        return self.default_language
    
    def translate_response_data(self, data: dict, language: str) -> dict:
        """Перевод данных ответа API"""
        if not isinstance(data, dict):
            return data
        
        translated_data = {}
        
        for key, value in data.items():
            # Переводим ключи сообщений
            if key in ['message', 'detail', 'error']:
                # Пытаемся найти перевод
                translation_key = f"api.{value.lower().replace(' ', '_')}"
                translated_value = self.get_translation(translation_key, language)
                
                # Если перевод найден (не равен ключу), используем его
                if translated_value != translation_key:
                    translated_data[key] = translated_value
                else:
                    translated_data[key] = value
            elif isinstance(value, dict):
                translated_data[key] = self.translate_response_data(value, language)
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                translated_data[key] = [self.translate_response_data(item, language) for item in value]
            else:
                translated_data[key] = value
        
        return translated_data

# Глобальный экземпляр сервиса i18n
i18n_service = I18nService() 