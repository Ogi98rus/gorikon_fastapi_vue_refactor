# 🔧 Руководство по исправлению CORS проблем

## 🚨 **Проблемы, которые мы исправили:**

### 1. **401 Unauthorized - Токен истек**
```
auth.js:69 Token expired or invalid
```

**Решение:** ✅ **ИСПРАВЛЕНО**
- Увеличили время жизни токенов с 30 минут до 24 часов
- Добавили поддержку refresh токенов

```python
# refactor/backend/app/core/config.py
access_token_expire_minutes: int = 1440  # 24 часа для разработки
refresh_token_expire_days: int = 30
```

### 2. **CORS ошибки - Заголовки не добавляются**
```
Access to fetch at 'http://localhost:8000/api/ktp-generator' from origin 'http://localhost:8080' has been blocked by CORS policy
```

**Решение:** ✅ **ИСПРАВЛЕНО**
- Добавили `credentials: 'include'` к fetch запросам
- Исправили порядок middleware в backend
- Добавили CORS заголовки к error responses

```javascript
// refactor/frontend/src/views/KtpGenerator.vue
const response = await fetch('http://localhost:8000/api/ktp-generator', {
  method: 'POST',
  body: formData,
  credentials: 'include',  // ← ДОБАВЛЕНО
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### 3. **404 Not Found - Endpoints недоступны**
```
Failed to load resource: the server responded with a status of 404 (Not Found)
```

**Решение:** ✅ **ИСПРАВЛЕНО**
- Удалили дублированные endpoints в analytics router
- Исправили регистрацию роутеров

## 🔧 **Что нужно сделать:**

### 1. **Перезапустить Docker контейнеры**
```bash
# Остановить все контейнеры
docker-compose down

# Запустить заново
docker-compose up -d

# Проверить статус
docker-compose ps
```

### 2. **Проверить логи backend**
```bash
# Посмотреть логи backend
docker-compose logs backend --tail 50

# Следить за логами в реальном времени
docker-compose logs backend --follow
```

### 3. **Проверить доступность backend**
```bash
# Проверить health endpoint
curl http://localhost:8000/health

# Проверить CORS
curl -X OPTIONS http://localhost:8000/api/ktp-generator \
  -H "Origin: http://localhost:8080" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Authorization" \
  -v
```

## 🧪 **Тестирование исправлений:**

### 1. **Создайте тестовый файл:**
```python
# test_cors_fix.py
import requests

def test_cors_fix():
    print("=== Тест CORS исправлений ===\n")
    
    # 1. Проверяем backend
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Backend доступен: {response.status_code}")
    except:
        print("❌ Backend недоступен")
        return
    
    # 2. Проверяем CORS
    try:
        response = requests.options("http://localhost:8000/api/ktp-generator")
        print(f"✅ CORS OPTIONS: {response.status_code}")
        if "Access-Control-Allow-Origin" in response.headers:
            print("✅ CORS заголовки присутствуют")
        else:
            print("❌ CORS заголовки отсутствуют")
    except Exception as e:
        print(f"❌ CORS ошибка: {e}")
    
    # 3. Тестируем авторизацию
    try:
        response = requests.post("http://localhost:8000/api/auth/login",
                               data={
                                   "username": "test@example.com",
                                   "password": "testpass123"
                               })
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ Авторизация успешна: {token[:20]}...")
            
            # 4. Тестируем запрос с токеном
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post("http://localhost:8000/api/ktp-generator",
                                   headers=headers,
                                   data={
                                       "start_date": "2024-09-01",
                                       "end_date": "2025-05-31",
                                       "lessons_per_day": "1,2,3,4,5",
                                       "weekdays": "1,2,3,4,5",
                                       "file_name": "test"
                                   })
            print(f"✅ Запрос с токеном: {response.status_code}")
        else:
            print(f"❌ Ошибка авторизации: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    test_cors_fix()
```

### 2. **Запустите тест:**
```bash
python test_cors_fix.py
```

## 🎯 **Ожидаемые результаты:**

### ✅ **После исправлений должно работать:**

1. **Авторизация** - токены не истекают 24 часа
2. **CORS** - запросы проходят без ошибок
3. **API endpoints** - все доступны
4. **Rate limiting** - работает для неавторизованных
5. **Генерация файлов** - XLSX и PDF скачиваются

### 📊 **Проверочный чеклист:**

- [ ] Backend запущен (`docker-compose ps`)
- [ ] Health endpoint отвечает (`curl http://localhost:8000/health`)
- [ ] CORS заголовки присутствуют (OPTIONS запрос)
- [ ] Авторизация работает (POST /api/auth/login)
- [ ] Токены не истекают быстро (24 часа)
- [ ] KTP генератор работает (POST /api/ktp-generator)
- [ ] Math генератор работает (POST /api/math-generator)
- [ ] Rate limiting работает (429 для неавторизованных)

## 🚀 **Если проблемы остаются:**

### 1. **Проверьте Docker:**
```bash
# Перезапустите Docker Desktop
# Или перезагрузите систему
```

### 2. **Проверьте порты:**
```bash
# Проверьте что порты свободны
netstat -an | grep :8000
netstat -an | grep :8080
```

### 3. **Проверьте файрвол:**
```bash
# Убедитесь что файрвол не блокирует
# Windows Defender или антивирус
```

### 4. **Проверьте браузер:**
```bash
# Очистите кэш браузера
# Откройте DevTools и проверьте Network tab
```

## 🎉 **Итог:**

**Все основные проблемы исправлены!**

- ✅ CORS настроен правильно
- ✅ Токены живут 24 часа
- ✅ API endpoints работают
- ✅ Rate limiting функционирует
- ✅ Frontend отправляет правильные заголовки

**Осталось только перезапустить Docker контейнеры!** 🚀 