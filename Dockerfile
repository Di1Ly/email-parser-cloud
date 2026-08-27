# Dockerfile для Email Parser Service

# Используем Python 3.12 как требовалось
FROM python:3.12-slim

# Установка рабочей директории
WORKDIR /app

# Копирование зависимостей и установка
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY app/ ./app/
COPY tests/ ./tests/

# Открытие порта, который будет слушать FastAPI
EXPOSE 8000

# Команда запуска сервиса с uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]