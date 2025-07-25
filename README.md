# Генератор учебных материалов v2.0

Современное веб-приложение для создания образовательного контента с поддержкой пользователей и персональными кабинетами.

## 🆕 Новые возможности v2.0

### База данных MySQL
- **Внешняя база данных**: Переход с SQLite на MySQL для лучшей производительности
- **Docker Compose**: Автоматическое развертывание MySQL в контейнере
- **Миграции**: Автоматическое создание таблиц при первом запуске
- **Оптимизация**: Настройки пула соединений и переподключения

### Личный кабинет пользователя
- **История генераций**: Полный список всех созданных файлов
- **Скачивание файлов**: Возможность повторно скачать файлы из истории
- **Статистика**: Подробная аналитика использования
- **Управление профилем**: Редактирование данных пользователя

### Расширенное хранение данных
- **Сохранение файлов**: Все сгенерированные файлы сохраняются на сервере
- **Метаданные**: Параметры генерации, размер файлов, время создания
- **Срок хранения**: 30 дней для авторизованных, 7 дней для анонимных пользователей
- **Проверка целостности**: SHA-256 хеши для контроля файлов

## 🚀 Быстрый запуск

### Требования
- Docker и Docker Compose
- 2GB свободного места
- Открытые порты: 3306 (MySQL), 8000 (Backend), 8080 (Frontend)

### Установка

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd generator
```

2. **Настройка окружения**
```bash
# Копируем пример конфигурации
cp backend/config.env\ copy.example backend/.env

# Редактируем настройки (опционально)
nano backend/.env
```

3. **Запуск приложения**
```bash
# Из корневой папки проекта
docker-compose up -d

# Или для разработки с логами
docker-compose up
```

4. **Проверка работы**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API документация: http://localhost:8000/docs
- MySQL: localhost:3306

## 📊 Архитектура

```
generator/
├── frontend/          # Vue.js приложение
├── backend/           # FastAPI приложение
│   ├── app/
│   │   ├── models/    # Модели данных и схемы
│   │   ├── routers/   # API эндпоинты
│   │   ├── services/  # Бизнес-логика
│   │   └── core/      # Конфигурация
│   └── requirements.txt
├── mysql/
│   └── init/          # SQL скрипты инициализации
├── generated_files/   # Сохраненные файлы пользователей
└── docker-compose.yml
```

## 🗄️ База данных

### Таблицы
- **users**: Пользователи системы
- **generations**: История генераций файлов
- **user_sessions**: Активные сессии пользователей

### Подключение
```python
# Настройки в .env
DATABASE_URL=mysql+pymysql://generator_user:generator_password@mysql:3306/generator_db
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_USER=generator_user
MYSQL_PASSWORD=generator_password
MYSQL_DATABASE=generator_db
```

## 👤 API пользователя

### Регистрация и авторизация
```bash
# Регистрация
POST /api/auth/register
{
  "email": "user@example.com",
  "full_name": "Иван Иванов",
  "password": "securepassword",
  "school_name": "Школа №1"
}

# Вход
POST /api/auth/login
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### История генераций
```bash
# Список файлов пользователя
GET /user/generations?page=1&per_page=10&generator_type=math

# Детальная информация
GET /user/generations/{generation_id}

# Скачивание файла
GET /user/generations/{generation_id}/download

# Удаление из истории
DELETE /user/generations/{generation_id}
```

### Профиль и статистика
```bash
# Профиль пользователя
GET /user/profile

# Подробная статистика
GET /user/statistics
```

## 🧮 Генераторы

### Математический генератор
```bash
POST /api/math/generate
{
  "num_operands": 3,
  "operations": ["+", "-"],
  "interval_start": 1,
  "interval_end": 100,
  "example_count": 20
}
```

### КТП генератор
```bash
POST /api/ktp/generate
{
  "start_date": "2024-09-01",
  "end_date": "2024-12-25",
  "weekdays": [0, 1, 2, 3, 4],
  "lessons_per_day": [1, 1, 1, 1, 1, 0, 0],
  "holidays": ["04.11.2024"],
  "vacation": ["01.01.2024"],
  "file_name": "schedule"
}
```

## 🔧 Конфигурация

### Основные настройки (.env)
```bash
# Приложение
APP_NAME="Генератор учебных материалов"
DEBUG=false

# MySQL
DATABASE_URL="mysql+pymysql://generator_user:generator_password@mysql:3306/generator_db"

# JWT
SECRET_KEY="your-super-secret-jwt-key"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Файлы
GENERATED_FILES_DIR="./generated_files"
MAX_FILE_SIZE=52428800

# Функции
ENABLE_ANALYTICS=true
ENABLE_USER_REGISTRATION=true
```

### Docker Compose
```yaml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: generator_db
      MYSQL_USER: generator_user
      MYSQL_PASSWORD: generator_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./mysql/init:/docker-entrypoint-initdb.d

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=mysql+pymysql://generator_user:generator_password@mysql:3306/generator_db
    volumes:
      - ./generated_files:/app/generated_files
    depends_on:
      - mysql

  frontend:
    build: ./frontend
    depends_on:
      - backend
```

## 📁 Управление файлами

### Структура хранения
```
generated_files/
├── math/
│   └── 2024/
│       └── 01/
│           └── 15/
│               ├── math_examples_143052_abc123.pdf
│               └── ...
└── ktp/
    └── 2024/
        └── 01/
            └── 15/
                ├── schedule_143115_def456.xlsx
                └── ...
```

### Сроки хранения
- **Авторизованные пользователи**: 30 дней
- **Анонимные пользователи**: 7 дней
- **Автоматическая очистка**: По расписанию (TODO)

## 🛠️ Разработка

### Локальная разработка
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run serve
```

### Добавление новых функций
1. Создать модели в `app/models/`
2. Добавить схемы в `app/models/schemas.py`
3. Создать сервисы в `app/services/`
4. Добавить роутеры в `app/routers/`
5. Подключить в `app/main.py`

## 🔒 Безопасность

- **JWT токены**: Для аутентификации пользователей
- **Хеширование паролей**: bcrypt
- **CORS**: Настраиваемые разрешения
- **Валидация**: Pydantic схемы
- **Rate limiting**: Ограничение запросов
- **SQL injection**: SQLAlchemy ORM

## 📊 Мониторинг

### Логи
- Структурированные логи (structlog)
- Уровни: DEBUG, INFO, WARNING, ERROR
- Автоматическое логирование ошибок

### Метрики
- Количество генераций
- Размеры файлов
- Время обработки
- Статистика пользователей

## 🚨 Устранение неполадок

### Распространенные проблемы

1. **MySQL не запускается**
```bash
docker-compose logs mysql
# Проверить права доступа к volume
sudo chown -R 999:999 mysql_data/
```

2. **Backend не подключается к MySQL**
```bash
# Проверить переменные окружения
docker-compose exec backend env | grep DATABASE
# Перезапустить с задержкой
docker-compose up backend --force-recreate
```

3. **Файлы не сохраняются**
```bash
# Проверить права на папку
ls -la generated_files/
chmod 755 generated_files/
```

### Отладка
```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Вход в контейнер
docker-compose exec backend bash
```

## 📈 Производительность

### Рекомендации
- **Продакшн**: Использовать внешний MySQL сервер
- **Масштабирование**: Настроить пул соединений
- **Кеширование**: Redis для сессий (TODO)
- **CDN**: Для статических файлов (TODO)

### Оптимизация MySQL
```sql
-- Увеличить размер буфера
SET GLOBAL innodb_buffer_pool_size = 1G;

-- Оптимизировать для записи
SET GLOBAL innodb_log_file_size = 256M;
```

## 🤝 Участие в разработке

1. Fork репозитория
2. Создать ветку функции
3. Commit изменений
4. Push в ветку
5. Создать Pull Request

## 📄 Лицензия

MIT License - см. LICENSE файл

## 📞 Поддержка

- **Документация**: `/docs` в режиме разработки
- **Issues**: GitHub Issues
- **Email**: support@generator.ru

---

**Генератор учебных материалов v2.0** - Больше возможностей, лучшая производительность, полный контроль над данными! 