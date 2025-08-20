# 🚀 Настройка Traefik для локального проксирования

## 📋 Что добавлено:

1. **Traefik контейнер** - автоматическое обнаружение сервисов
2. **Сеть traefik** - изолированная сеть для сервисов
3. **Labels** - автоматическая настройка маршрутов
4. **HTTP прокси** - для внутренней маршрутизации

## 🔧 Запуск:

```bash
# Создаем сеть (если не существует)
docker network create traefik

# Запускаем все сервисы
docker-compose up -d

# Проверяем статус
docker-compose ps
```

## 🌐 Доступ к сервисам:

- **Traefik Dashboard**: http://localhost:8080
- **Фронтенд**: http://localhost (через Traefik)
- **API**: http://localhost/api/ (через Traefik)

## 🔗 Подключение через nginx proxy manager:

### Настройка в nginx proxy manager:
- **Домен**: `gorikon.ru`
- **Прокси**: `http://ВАШ_IP:80/` (порт 80 - Traefik)
- **SSL**: Включить (nginx proxy manager получит сертификат)
- **WebSocket Support**: Включить (если нужно)

### Как это работает:
1. **Traefik** работает локально на порту 80
2. **nginx proxy manager** подключается к порту 80
3. **Traefik** автоматически маршрутизирует запросы по labels
4. **SSL** и внешний доступ обеспечивает nginx proxy manager

## 📝 Labels в сервисах:

### Backend:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.backend.rule=Host(`gorikon.ru`) && PathPrefix(`/api/`)"
  - "traefik.http.services.backend.loadbalancer.server.port=8000"
```

### Frontend:
```yaml
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.frontend.rule=Host(`gorikon.ru`)"
  - "traefik.http.services.frontend.loadbalancer.server.port=80"
```

## 🔍 Проверка работы:

1. **Traefik логи**:
```bash
docker-compose logs traefik
```

2. **Проверка маршрутов**:
```bash
curl -H "Host: gorikon.ru" http://localhost/api/docs
```

3. **Проверка фронтенда**:
```bash
curl -H "Host: localhost" http://localhost/
```

4. **Проверка API**:
```bash
curl -H "Host: localhost" http://localhost/api/docs
```

## ⚠️ Важно:

- Убедитесь, что домен `gorikon.ru` указывает на ваш сервер
- Порт 80 должен быть открыт в файрволле (для Traefik)
- Порт 443 должен быть открыт в файрволле (для nginx proxy manager)
- SSL сертификат получает nginx proxy manager, а не Traefik

## 🎯 Преимущества Traefik:

✅ **Автоматическое обнаружение** сервисов  
✅ **Простая HTTP маршрутизация**  
✅ **Встроенный балансировщик нагрузки**  
✅ **Мониторинг и метрики**  
✅ **Простая конфигурация** через labels
