# database.models.py    # SQLAlchemy

from datetime import date, datetime
from sqlalchemy import Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Базовый класс для всех моделей. Это паттерн ООП: наследование общей логики.
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # index=True ускоряет поиск по нику, что критично при частых запросах от бота
    telegram_username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Связь "один ко многим": у одного пользователя много задач
    tasks: Mapped[list["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    # Тип задачи: 'planting', 'watering', 'motoblock', 'harvest' и т.д.
    task_type: Mapped[str] = mapped_column(String(50), default="general")

    user: Mapped["User"] = relationship(back_populates="tasks")


class CropReminder(Base):
    __tablename__ = "crop_reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Например, "Томаты"
    month: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-12
    tip_text: Mapped[str] = mapped_column(Text, nullable=False)  # "Пора высаживать рассаду в теплицу"