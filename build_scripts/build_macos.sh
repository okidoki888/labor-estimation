#!/bin/bash
# Скрипт сборки для macOS
# Создаёт .app bundle (onedir режим)

echo "===================================="
echo "Сборка приложения для macOS"
echo "===================================="

# Переходим в корневую директорию проекта
cd "$(dirname "$0")/.."

# Проверка виртуального окружения
if [ -d "venv" ]; then
    echo "Активация venv..."
    source venv/bin/activate
fi

# Проверка наличия PyInstaller
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "Установка PyInstaller..."
    pip install pyinstaller
fi

# Запускаем сборку через spec-файл (включает hiddenimports, корректный .app)
echo "Сборка приложения..."
pyinstaller labor_estimation.spec

echo "===================================="
echo "Сборка завершена!"
echo "Приложение: dist/LabLaborEstimation.app"
echo "===================================="
