# bot/main.py
# инициализируем диспетчер (Dispatcher), подключаем роутеры и корректно запускаем/останавливаем асинхронный клиент.

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

from bot.handlers import user
from bot.services.api_client import api_client

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    logger.info(f"Бот запущен! @{(await bot.get_me()).username}")


async def on_shutdown(bot: Bot):
    logger.info("Бот останавливается, закрываем соединения...")
    await api_client.close()  # Важно закрыть httpx клиент


async def main():
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    if not token:
        logger.error("❌ Не найден BOT_TOKEN в файле .env")
        return

    # Инициализируем бота с настройками по умолчанию (например, Markdown для всех сообщений)
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )

    # Инициализируем диспетчер
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(user.router)

    # Регистрируем колбэки на запуск и остановку
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("🚀 Запускаем polling...")
    try:
        # start_polling() - это асинхронная функция, которая блокирует выполнение
        # до тех пор, пока бот работает, но НЕ блокирует event loop для обработки событий.
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # asyncio.run создает новый event loop и запускает в нем нашу главную асинхронную функцию
    asyncio.run(main())
