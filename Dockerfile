FROM ubuntu:24.04

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-4.0 \
    libgtk-4-dev \
    curl \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Копируем файлы проекта
WORKDIR /app
COPY . /app

# Устанавливаем зависимости через uv
RUN uv pip install -e .

# Запускаем приложение
CMD ["python3", "docker_gui.py"]