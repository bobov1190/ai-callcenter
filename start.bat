@echo off
chcp 65001 > nul
echo 🚀 Запуск AI Call Center...

REM Проверка виртуального окружения
if not exist "env\" (
    echo ❌ Виртуальное окружение не найдено!
    echo Создайте его: python -m venv env
    pause
    exit /b 1
)

REM Активация виртуального окружения
call env\Scripts\activate.bat

REM Проверка .env файла
if not exist ".env" (
    echo ❌ Файл .env не найден!
    echo Скопируйте .env.example в .env и настройте его
    pause
    exit /b 1
)

REM Запуск сервера
echo ✅ Запуск сервера на http://localhost:8000
python main.py

pause
