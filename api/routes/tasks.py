# api/routes/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.engine import get_db_session
from database.models import Task, User
from api.schemas import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
async def create_task(
        task_data: TaskCreate,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Создание новой задачи для пользователя.
    Сначала находим пользователя по username, затем создаем задачу.
    """
    # Находим пользователя
    result = await session.execute(
        select(User).where(User.telegram_username == task_data.telegram_username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")

    # Создаем задачу
    new_task = Task(
        user_id=user.id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        task_type=task_data.task_type
    )
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return new_task


@router.get("/", response_model=list[TaskResponse])
async def get_user_tasks(
        telegram_username: str,
        completed: bool | None = None,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Получение списка задач пользователя.
    Параметр completed позволяет фильтровать задачи (выполненные/невыполненные).
    """
    # Находим пользователя
    result = await session.execute(
        select(User).where(User.telegram_username == telegram_username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Формируем запрос с учетом фильтра
    query = select(Task).where(Task.user_id == user.id)
    if completed is not None:
        query = query.where(Task.is_completed == completed)

    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_update: TaskUpdate,
        session: AsyncSession = Depends(get_db_session)
):
    """
    Обновление задачи (например, отметка о выполнении).
    Используем PATCH, так как обновляем только указанные поля.
    """
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Обновляем только те поля, которые были переданы
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)

    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
        task_id: int,
        session: AsyncSession = Depends(get_db_session)
):
    """Удаление задачи"""
    result = await session.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()

    return None