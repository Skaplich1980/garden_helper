# -*- coding: utf-8 -*-
# database.init_db.py   # создаёт таблицы перед запуском приложения

import asyncio
from database.engine import engine
from database.models import Base

async def init_db():
    """
    Асинхронная инициализация базы данных.
    Создает все таблицы, описанные в моделях, если их еще не существует.
    """
    print("Initializing database...")
    async with engine.begin() as conn:
        # run_sync используется потому, что метод create_all в SQLAlchemy
        # исторически является синхронным. run_sync безопасно выполняет его
        # в отдельном потоке, не блокируя главный асинхронный цикл (event loop).
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialized successfully!")

if __name__ == "__main__":
    # Запускаем асинхронную функцию из синхронного контекста (при прямом запуске скрипта)
    asyncio.run(init_db())
