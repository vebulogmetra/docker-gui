# Docker GUI AppImage

Этот каталог содержит файлы для создания автономного AppImage приложения Docker GUI с современным GTK4 интерфейсом.

## Структура файлов

- `AppRun` - скрипт запуска приложения в AppImage
- `docker-gui.desktop` - файл интеграции с системой
- `build.sh` - скрипт сборки AppImage
- `create_icon.py` - генератор современной иконки приложения
- `icon.png` - иконка приложения (создается автоматически)

## Требования для сборки

### Системные зависимости
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-dev build-essential libgtk-4-dev

# CentOS/RHEL/Fedora
sudo dnf install python3-pip python3-devel gcc gtk4-devel

# Arch Linux
sudo pacman -S python-pip base-devel gtk4
```

### Python зависимости
```bash
# Установка зависимостей через uv
uv add pyinstaller pillow pygobject psutil docker
```

### AppImage инструменты
```bash
# Скачать appimagetool
wget -O appimagetool "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
chmod +x appimagetool
sudo mv appimagetool /usr/local/bin/
```

## Процесс сборки

### 1. Создание иконки
```bash
cd appimage
python3 create_icon.py
```

### 2. Сборка AppImage
```bash
chmod +x build.sh
./build.sh
```

### 3. Результат
После успешной сборки AppImage будет создан в директории `dist/`:
```
dist/docker-gui-0.1.0-x86_64.AppImage
```

## Использование AppImage

### Запуск
```bash
# Сделать исполняемым
chmod +x dist/docker-gui-0.1.0-x86_64.AppImage

# Запустить
./dist/docker-gui-0.1.0-x86_64.AppImage
```

### Установка в систему
```bash
# Скопировать в /usr/local/bin для глобального доступа
sudo cp dist/docker-gui-0.1.0-x86_64.AppImage /usr/local/bin/docker-gui
sudo chmod +x /usr/local/bin/docker-gui

# Создать символическую ссылку
sudo ln -sf /usr/local/bin/docker-gui /usr/local/bin/docker-gui.AppImage
```

## Особенности AppImage

### Автономность
- Включает Python runtime
- Включает все необходимые GTK4 библиотеки
- Включает Docker API клиент
- Не требует установки дополнительных зависимостей

### Совместимость
- Работает на большинстве Linux дистрибутивов
- Не требует root прав для установки
- Портативный формат
- Поддержка GTK4 для современного интерфейса

### Ограничения
- Требует Docker, установленный в системе
- Размер файла может быть большим (150-250MB)
- Первый запуск может быть медленным

## Устранение неполадок

### Ошибка "Docker not found"
Убедитесь, что Docker установлен и запущен:
```bash
# Проверить установку Docker
docker --version

# Запустить Docker daemon
sudo systemctl start docker
sudo systemctl enable docker

# Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

### Ошибка "Permission denied"
```bash
# Сделать AppImage исполняемым
chmod +x docker-gui-0.1.0-x86_64.AppImage
```

### Ошибка "GTK4 not found"
AppImage включает все необходимые GTK4 библиотеки. Если проблема остается:
```bash
# Установить GTK4 в системе
sudo apt install libgtk-4-1 libgtk-4-dev
```

### Ошибка "Python modules not found"
```bash
# Убедиться, что все зависимости установлены
uv sync
```

## Настройка сборки

### Изменение версии
Отредактируйте переменную `VERSION` в файле `build.sh`:
```bash
VERSION="0.2.0"  # Изменить на нужную версию
```

### Добавление дополнительных файлов
Отредактируйте секцию `datas` в `build.sh`:
```python
datas=[
    ('ui/', 'ui/'),
    ('core/', 'core/'),
    ('services/', 'services/'),
    ('resources/', 'resources/'),
    ('README.md', '.'),
    ('pyproject.toml', '.'),
    ('additional_file.txt', '.'),  # Добавить новые файлы
],
```

### Оптимизация размера
Для уменьшения размера AppImage:
1. Используйте UPX для сжатия (уже включено)
2. Исключите ненужные модули в `excludes`
3. Используйте `--strip` для удаления отладочной информации
4. Настройте `hiddenimports` для включения только необходимых модулей

## Интеграция с CI/CD

### GitHub Actions
```yaml
name: Build AppImage
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install uv
      uses: astral-sh/setup-uv@v1
    - name: Install dependencies
      run: |
        uv add pyinstaller pillow pygobject psutil docker
        wget -O appimagetool "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
        chmod +x appimagetool
        sudo mv appimagetool /usr/local/bin/
    - name: Build AppImage
      run: |
        cd appimage
        python3 create_icon.py
        chmod +x build.sh
        ./build.sh
    - name: Upload AppImage
      uses: actions/upload-artifact@v4
      with:
        name: docker-gui-appimage
        path: dist/*.AppImage
```

## Новые возможности

### GTK4 поддержка
- Современный интерфейс с GTK4
- Улучшенная производительность
- Лучшая интеграция с современными дистрибутивами

### Оптимизация памяти
- Встроенный мониторинг памяти
- Автоматическая очистка кэшей
- Оптимизированная загрузка данных

### Улучшенная иконка
- Современный дизайн с градиентами
- Тени и скругленные углы
- Профессиональный внешний вид 