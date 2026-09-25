# database.engine.py
# Здесь мы настраиваем подключение к SQLite так, чтобы оно не блокировало event loop.

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

# URL базы данных. Префикс "sqlite+aiosqlite" указывает SQLAlchemy использовать
# асинхронный драйвер aiosqlite, а не стандартный синхронный sqlite3.
# Файл garden.db будет создан в корне проекта.
DATABASE_URL = "sqlite+aiosqlite:///./garden.db"

# Создаем асинхронный движок.
# echo=True полезен при разработке: он выводит все SQL-запросы в консоль,
# что помогает учиться и отлаживать работу ORM.
engine = create_async_engine(DATABASE_URL, echo=True) # фоновый поток, а наш код продолжает выполняться асинхронно, ожидая результат через await

# Фабрика сессий. Мы будем использовать её для выполнения запросов к БД.
# expire_on_commit=False предотвращает ошибки доступа к объектам после закрытия сессии.
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Функция-помощник для получения сессии (паттерн Dependency Injection, который мы используем в FastAPI)
async def get_db_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session