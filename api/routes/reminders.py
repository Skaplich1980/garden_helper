from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database.engine import get_db_session
from database.models import CropReminder
from api.schemas import CropReminderResponse

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/", response_model=List[CropReminderResponse])
async def get_reminders(
    month: int = Query(..., ge=1, le=12, description="Номер месяца (1-12)"),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Получение сезонных рекомендаций для указанного месяца.
    """
    result = await session.execute(
        select(CropReminder)
        .where(CropReminder.month == month)
        .order_by(CropReminder.crop_name)
    )
    reminders = result.scalars().all()
    
    if not reminders:
        return []
    
    return reminders
