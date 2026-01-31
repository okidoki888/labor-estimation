@echo off
REM Скрипт сборки для Windows
REM Создаёт standalone exe файл (onefile)

chcp 65001 >nul
echo ====================================
echo Сборка приложения для Windows
echo ====================================

REM Переходим в корневую директорию проекта
cd /d "%~dp0.."

REM Проверка виртуального окружения
if exist "venv\Scripts\activate.bat" (
    echo Активация venv...
    call venv\Scripts\activate.bat
)

REM Проверка наличия PyInstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Установка PyInstaller...
    pip install pyinstaller
)

REM Запускаем сборку через spec-файл
echo Сборка приложения...
pyinstaller labor_estimation.spec

echo ====================================
echo Сборка завершена!
echo Исполняемый файл: dist\LabLaborEstimation.exe
echo ====================================
pause
