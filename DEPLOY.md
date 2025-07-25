# Быстрое развертывание

## 🚀 За 3 минуты

```bash
# 1. Клонируем и переходим в папку
git clone <repository-url>
cd generator/refactor

# 2. Копируем конфигурацию
cp backend/config.env\ copy.example backend/.env

# 3. Запускаем
docker-compose up -d

# 4. Проверяем
curl http://localhost:8000/health
```

## 📋 Результат

- **Frontend**: http://localhost:8080
- **Backend**: http://localhost:8000  
- **API Docs**: http://localhost:8000/docs
- **MySQL**: localhost:3306

## 🔧 Настройка (опционально)

### Изменить пароли MySQL
```bash
# Редактируем .env
nano backend/.env

# Меняем строки:
MYSQL_PASSWORD=your_secure_password
SECRET_KEY=your-super-secret-jwt-key
```

### Персонализация
```bash
# В backend/.env
APP_NAME="Название вашего приложения"
EMAIL_FROM=your-email@domain.com
```

## 📊 Проверка работы

```bash
# Статус всех сервисов
docker-compose ps

# Логи
docker-compose logs -f

# Остановка
docker-compose down

# Полная очистка
docker-compose down -v
docker system prune -f
```

## 🔐 Первый пользователь

```bash
# Регистрация через API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "full_name": "Администратор",
    "password": "securepassword123",
    "school_name": "Тестовая школа"
  }'
```

## ⚠️ Решение проблем

### MySQL не запускается
```bash
# Права доступа
sudo chown -R 999:999 ./mysql_data

# Очистка volume
docker-compose down -v
docker-compose up mysql
```

### Backend не подключается
```bash
# Ждем запуска MySQL
docker-compose up mysql
sleep 30
docker-compose up backend
```

### Порты заняты
```bash
# Изменить порты в docker-compose.yml
ports:
  - "3307:3306"  # MySQL
  - "8001:8000"  # Backend  
  - "8081:80"    # Frontend
```

---

**Готово!** Приложение работает и готово к использованию. 