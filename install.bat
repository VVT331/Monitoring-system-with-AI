@echo off
chcp 65001 >nul

echo ================================================
echo  Установка зависимостей для проекта "Мониторинг ИБ"
echo ================================================
echo.

python -m pip install --upgrade pip

pip install psutil watchdog schedule requests plyer

echo.
echo ================================================
echo  Установка успешно завершена!
echo.
echo  Теперь можно запускать программу:
echo  python gui.py
echo.
pause