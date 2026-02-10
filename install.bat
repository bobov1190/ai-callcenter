@echo off
chcp 65001 > nul
echo 📦 Обновление зависимостей...

if not exist "env\" (
    echo ❌ Виртуальное окружение не найдено!
    echo Создание нового виртуального окружения...
    python -m venv env
)

call env\Scripts\activate.bat
echo ✅ Установка/обновление зависимостей...
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Готово!
pause
