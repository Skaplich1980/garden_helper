@echo off
echo ?? Запуск Огородного Помощника...
echo.

start "API Server" cmd /k "python -m api.main"
timeout /t 2 /nobreak >nul
start "Telegram Bot" cmd /k "python -m bot.main"

echo ? Оба сервиса запущены в отдельных окнах
pause