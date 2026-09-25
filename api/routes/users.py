# api/routes/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.engine import get_db_session
from database.models import User
from api.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(
        user_data: UserCreate,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Регистрация нового пользователя или получение существующего.
    Это асинхронная функция (async def), потому что она выполняет I/O операции
    (запись в БД), которые не должны блокировать event loop.
    """
    # Проверяем, существует ли пользователь
    result = await session.execute(
        select(User).where(User.telegram_username == user_data.telegram_username)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # Если пользователь уже есть, просто возвращаем его
        return existing_user

    # Создаем нового пользователя
    new_user = User(telegram_username=user_data.telegram_username)
    session.add(new_user)

    # await commit() - асинхронная операция записи в БД
    # Пока идет запись, event loop может обрабатывать другие запросы
    await session.commit() #  асинхронная запись в БД. Это не блокирует поток.
    await session.refresh(new_user)

    return new_user


@router.get("/{telegram_username}", response_model=UserResponse)
async def get_user(
        telegram_username: str,
        session: AsyncSession = Depends(get_db_session) #  паттерн Dependency Injection.
        # FastAPI автоматически создает сессию БД для каждого запроса и закрывает её после выполнения.
):
    """Получение пользователя по telegram_username"""
    result = await session.execute( # SQLAlchemy выполняет SQL-запрос к SQLite
        select(User).where(User.telegram_username == telegram_username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user