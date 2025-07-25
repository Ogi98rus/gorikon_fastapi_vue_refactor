FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем и устанавливаем зависимости ДО создания пользователя
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Создаем временную директорию
RUN mkdir -p temp

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности и меняем владельца файлов
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Переключаемся на appuser только в самом конце
USER appuser

# Настройки по умолчанию
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открываем порт
EXPOSE 8000

# Команда запуска с новой структурой
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 