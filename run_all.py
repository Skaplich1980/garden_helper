# run_all.py
"""
Универсальный раннер для запуска всех компонентов проекта.
Использует asyncio для одновременного запуска API и бота.
"""
import asyncio
import sys
import os
import uvicorn

# Добавляем корень проекта в sys.path, чтобы импорты работали
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def run_api():
    """Запуск FastAPI сервера через uvicorn"""
    print("🌐 [API] Запуск FastAPI сервера на http://127.0.0.1:8000")
    config = uvicorn.Config(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def run_bot():
    """Запуск Telegram-бота"""
    # Небольшая задержка, чтобы API успел стартовать
    await asyncio.sleep(2)
    print("🤖 [BOT] Запуск Telegram-бота...")

    from bot.main import main as bot_main
    await bot_main()


async def main():
    print("=" * 60)
    print(" Огородный Помощник - запуск всех сервисов")
    print("=" * 60)

    # Запускаем оба процесса параллельно
    await asyncio.gather(
        run_api(),
        run_bot(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Остановка всех сервисов...")