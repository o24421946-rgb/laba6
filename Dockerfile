# Используем базовый образ Python
FROM python:3.12-slim

# Устанавливаем системные зависимости для pygame и X11
RUN apt-get update && apt-get install -y \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    libv4l-dev \
    x11-apps \
    xauth \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем переменную окружения для pygame
ENV SDL_VIDEODRIVER=x11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY logic.py gui.py ./

# Устанавливаем переменные окружения
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Точка входа - запуск игры
CMD ["python", "gui.py"]

