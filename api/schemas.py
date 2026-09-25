# api/schemas.py

from datetime import date, datetime
from pydantic import BaseModel, Field

# === Схемы для пользователей ===

class UserCreate(BaseModel):
    """Схема для создания нового пользователя"""
    telegram_username: str = Field(..., min_length=1, max_length=100)

class UserResponse(BaseModel):
    """Схема ответа с данными пользователя"""
    id: int
    telegram_username: str
    created_at: datetime

    model_config = {"from_attributes": True}

# === Схемы для задач ===

class TaskCreate(BaseModel):
    """Схема для создания новой задачи"""
    telegram_username: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    due_date: date | None = None
    task_type: str = Field(default="general", max_length=50)

class TaskUpdate(BaseModel):
    """Схема для обновления задачи (например, отметка о выполнении)"""
    is_completed: bool | None = None
    title: str | None = None
    description: str | None = None

class TaskResponse(BaseModel):
    """Схема ответа с данными задачи"""
    id: int
    user_id: int
    title: str
    description: str | None
    due_date: date | None
    is_completed: bool
    task_type: str

    model_config = {"from_attributes": True}

# === Схемы для сезонных рекомендаций ===

class CropReminderResponse(BaseModel):
    """Схема ответа с сезонной рекомендацией"""
    id: int
    crop_name: str
    month: int
    tip_text: str

    model_config = {"from_attributes": True}
