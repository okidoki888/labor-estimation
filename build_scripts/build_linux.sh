#!/bin/bash
# Скрипт сборки для Linux
# Создаёт standalone бинарник (onefile)

echo "===================================="
echo "Сборка приложения для Linux"
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

# Запускаем сборку через spec-файл
echo "Сборка приложения..."
pyinstaller labor_estimation.spec

echo "===================================="
echo "Сборка завершена!"
echo "Исполняемый файл: dist/LabLaborEstimation"
echo "===================================="
