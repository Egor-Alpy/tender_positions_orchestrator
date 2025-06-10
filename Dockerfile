FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY src/ ./src/

# Создание пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Переменная окружения для Python
ENV PYTHONPATH=/app

# Порт
EXPOSE 8000

# Запуск
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]