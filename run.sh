#!/bin/bash

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Docker GUI - Новое приложение${NC}"
echo -e "${BLUE}==============================${NC}"

# Проверка Python
echo -e "${YELLOW}Проверка Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION найден${NC}"

# Проверка uv
echo -e "${YELLOW}Проверка uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv не найден${NC}"
    echo -e "${YELLOW}Установите uv: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ uv найден${NC}"

# Проверка Docker
echo -e "${YELLOW}Проверка Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не найден${NC}"
    echo -e "${YELLOW}Установите Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
echo -e "${GREEN}✅ Docker $DOCKER_VERSION найден${NC}"

# Проверка Docker daemon
echo -e "${YELLOW}Проверка Docker daemon...${NC}"
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon не запущен${NC}"
    echo -e "${YELLOW}Запустите Docker daemon: sudo systemctl start docker${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker daemon запущен${NC}"

# Проверка зависимостей
echo -e "${YELLOW}Проверка зависимостей...${NC}"
if ! uv run python3 -c "import gi; gi.require_version('Gtk', '4.0')" &> /dev/null; then
    echo -e "${RED}❌ GTK4 не найден${NC}"
    echo -e "${YELLOW}Установите GTK4: sudo apt install libgtk-4-1 python3-gi${NC}"
    exit 1
fi

echo -e "${GREEN}✅ GTK4 найден${NC}"

# Установка зависимостей Python
echo -e "${YELLOW}Установка зависимостей Python...${NC}"
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}Создание виртуального окружения...${NC}"
    uv venv
fi

echo -e "${BLUE}Установка зависимостей...${NC}"
uv pip install PyGObject

# Проверка файлов приложения
echo -e "${YELLOW}Проверка файлов приложения...${NC}"

REQUIRED_FILES=(
    "main.py"
    "docker_api.py"
    "core/__init__.py"
    "core/resource_manager.py"
    "core/resource_view.py"
    "core/base_operations.py"
    "services/__init__.py"
    "services/docker_service.py"
    "services/notification_service.py"
    "resources/__init__.py"
    "resources/containers.py"
    "resources/images.py"
    "resources/networks.py"
    "resources/volumes.py"
    "ui/components/__init__.py"
    "ui/themes/__init__.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Файл $file не найден${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Все файлы приложения найдены${NC}"

# Запуск приложения
echo -e "${BLUE}🚀 Запуск Docker GUI...${NC}"
echo -e "${BLUE}==============================${NC}"

# Запуск приложения
echo -e "${BLUE}Запуск через uv...${NC}"
uv run python3 main.py

echo -e "${GREEN}✅ Приложение завершено${NC}" 