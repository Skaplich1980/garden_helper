"""
Конфигурация для тестов.
Переопределяем сессию БД на тестовую базу в памяти.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient

from database.models import Base
from database.engine import get_db_session
from api.main import app


# Тестовая база в памяти (не файл на диске)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем движок и сессии
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db_session() -> AsyncSession:
    """Переопределение зависимости get_db_session для тестов"""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Создаём таблицы перед каждым тестом и удаляем после"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """Создаёт тестовый клиент FastAPI с переопределённой зависимостью БД"""
    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def db_session():
    """Сессия БД для прямого доступа к модели"""
    async with TestSessionLocal() as session:
        yield session
