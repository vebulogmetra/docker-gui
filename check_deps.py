#!/usr/bin/env python3
import subprocess
import os

def print_colored(text, color_code):
    """Печатает текст с указанным цветом."""
    print(f"\033[{color_code}m{text}\033[0m")

def print_error(text):
    """Печатает ошибку красным цветом."""
    print_colored(text, 91)

def print_warning(text):
    """Печатает предупреждение желтым цветом."""
    print_colored(text, 93)

def print_success(text):
    """Печатает успешное сообщение зеленым цветом."""
    print_colored(text, 92)

def print_info(text):
    """Печатает информационное сообщение голубым цветом."""
    print_colored(text, 96)

def check_command(command):
    """Проверяет доступность команды в системе."""
    try:
        subprocess.run(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True, 
            shell=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def check_python_package(package):
    """Проверяет, установлен ли Python пакет."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_package(package):
    """Устанавливает системный пакет через apt."""
    print_info(f"Установка пакета {package}...")
    try:
        subprocess.run(
            f"sudo apt-get install -y {package}",
            shell=True,
            check=True
        )
        print_success(f"Пакет {package} успешно установлен.")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Не удалось установить пакет {package}.")
        return False

def install_uv():
    """Устанавливает менеджер пакетов uv."""
    print_info("Установка uv...")
    try:
        subprocess.run(
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
            shell=True,
            check=True
        )
        print_success("uv успешно установлен.")

        # Добавляем путь к uv в PATH для текущей сессии
        uv_bin = os.path.expanduser("~/.cargo/bin")
        if uv_bin not in os.environ["PATH"]:
            os.environ["PATH"] += f":{uv_bin}"

        return True
    except subprocess.CalledProcessError:
        print_error("Не удалось установить uv.")
        return False

def install_python_package(package):
    """Устанавливает Python пакет через uv."""
    print_info(f"Установка Python пакета {package}...")
    try:
        if check_command("uv"):
            subprocess.run(
                f"uv pip install {package}",
                shell=True,
                check=True
            )
        else:
            subprocess.run(
                f"pip3 install {package}",
                shell=True,
                check=True
            )
        print_success(f"Пакет {package} успешно установлен.")
        return True
    except subprocess.CalledProcessError:
        print_error(f"Не удалось установить пакет {package}.")
        return False

def main():
    print_info("Проверка зависимостей Docker GUI...")
    # Проверка Python
    print_info("Проверка Python...")
    if not check_command("python3 --version"):
        print_error("Python 3 не установлен.")
        install_package("python3")
    else:
        print_success("Python 3 установлен.")

    # Проверка GTK
    print_info("Проверка GTK...")
    gtk_packages = ["python3-gi", "python3-gi-cairo", "gir1.2-gtk-4.0"]
    for package in gtk_packages:
        if not check_command(f"dpkg -l | grep {package}"):
            print_warning(f"Пакет {package} не установлен.")
            install_package(package)
        else:
            print_success(f"Пакет {package} установлен.")

    # Проверка Docker
    print_info("Проверка Docker...")
    if not check_command("docker --version"):
        print_error("Docker не установлен.")
        install_package("docker.io")
    else:
        print_success("Docker установлен.")

    # Проверка доступа к Docker демону
    print_info("Проверка доступа к Docker демону...")
    if not check_command("docker info"):
        print_warning("Нет доступа к Docker демону. Добавление пользователя в группу docker...")
        try:
            user = os.environ.get("USER")
            subprocess.run(
                f"sudo usermod -aG docker {user}",
                shell=True,
                check=True
            )
            print_warning("Пользователь добавлен в группу docker. Перезайдите в систему или выполните 'newgrp docker'.")
        except subprocess.CalledProcessError:
            print_error("Не удалось добавить пользователя в группу docker.")
    else:
        print_success("Доступ к Docker демону есть.")

    # Проверка uv
    print_info("Проверка uv...")
    if not check_command("uv --version"):
        print_warning("uv не установлен.")
        install_uv()
    else:
        print_success("uv установлен.")

    # Проверка Python пакетов
    print_info("Проверка Python пакетов...")
    python_packages = ["docker"]  # gi устанавливается через системные пакеты
    for package in python_packages:
        if not check_python_package(package):
            print_warning(f"Python пакет {package} не установлен.")
            install_python_package(package)
        else:
            print_success(f"Python пакет {package} установлен.")

    # Проверка gi отдельно, так как это системный пакет
    print_info("Проверка модуля gi...")
    try:
        import gi
        print_success("Модуль gi доступен.")
    except ImportError:
        print_warning("Модуль gi не найден. Убедитесь, что пакет python3-gi установлен корректно.")
        print_info("Попытка переустановки пакетов GTK...")
        for package in gtk_packages:
            install_package(package)
    print_info("Все зависимости установлены. Можно запускать приложение Docker GUI.")

if __name__ == "__main__":
    main()
