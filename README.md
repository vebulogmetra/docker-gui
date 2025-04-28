# Docker GUI

Графическое приложение для управления Docker на Ubuntu 24.04 с использованием GTK4.

## Возможности

- Просмотр списка Docker образов (images)
- Просмотр запущенных и остановленных контейнеров
- Просмотр Docker сетей
- Просмотр Docker томов (volumes)
- Удаление образов
- Остановка и удаление контейнеров

## Требования

- Ubuntu 24.04
- Python 3.10+
- Docker
- GTK 4

## Установка

1. Установите зависимости системы:

```
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 docker.io
```

2. Установите `uv` согласно [официальной документации](https://github.com/astral-sh/uv):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Клонируйте репозиторий:

```
git clone https://github.com/yourusername/docker-gui.git
cd docker-gui
```

4. Установите зависимости проекта с помощью `uv`:

```
uv venv .venv
```

```
source .venv/bin/activate
```

```
uv pip install -e .
```

## Запуск приложения

Рекомендуемый способ запуска (с проверкой зависимостей и созданием виртуального окружения)

```
bash run.sh
```

Запуск используя системный python

```
python3 docker_gui.py
```

Если у вас установлен `uv`, можно запустить через:

```
uv run docker_gui.py
```

## Устранение проблем

### Ошибка "Import 'gi' could not be resolved"

Несмотря на предупреждения IDE о проблемах с импортом модуля `gi`, приложение должно работать корректно.
Если PyCharm или VS Code показывают ошибки, вы можете:

1. Добавить в файл `pyproject.toml` строку:
```
[tool.pyright]
reportMissingModuleSource = false
```

2. Или установить `pygobject-stubs`:
```
pip install pygobject-stubs --config-settings=config=Gtk4
```

### Проблемы с правами доступа к Docker

Если приложение не может подключиться к Docker API, убедитесь что ваш пользователь имеет права на доступ:

```
sudo usermod -aG docker $USER
newgrp docker
```

## Лицензия

MIT
