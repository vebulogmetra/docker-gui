#!/bin/bash

# Проверка установки зависимостей
command -v python3 >/dev/null 2>&1 || { echo "Требуется Python 3. Установите с помощью: sudo apt install python3"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Требуется Docker. Установите с помощью: sudo apt install docker.io"; exit 1; }

# Проверяем, установлен ли GTK4
if ! dpkg -l | grep -q "gir1.2-gtk-4.0"; then
    echo "GTK4 не установлен. Установка..."
    sudo apt-get update && sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-4.0
fi

# Проверяем наличие uv
if ! command -v uv >/dev/null 2>&1; then
    echo "uv не найден. Установка..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Проверяем, установлены ли зависимости проекта
if [ ! -d ".venv" ] || [ ! -f ".venv/pyvenv.cfg" ]; then
    echo "Установка зависимостей проекта..."
    uv pip install -e .
    uv pip install docker pygobject
fi

# Запускаем скрипт проверки зависимостей
echo "Запуск скрипта проверки зависимостей..."
python3 check_deps.py

# Запускаем приложение
echo "Запуск Docker GUI..."
uv run docker_gui.py 