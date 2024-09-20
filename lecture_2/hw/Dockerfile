# Используем базовый образ с Python
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем всё приложение
COPY . /app

# Открываем порт, на котором работает Uvicorn
EXPOSE 8080

# Запуск приложения с помощью Uvicorn
CMD ["uvicorn", "shop_api.main:app", "--host", "0.0.0.0", "--port", "8080"]