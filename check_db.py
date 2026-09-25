import asyncio
from database.models import CropReminder
from database.engine import async_session_maker

async def main():
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(CropReminder))
        reminders = result.scalars().all()
        print(f"Total reminders: {len(reminders)}")
        if reminders:
            print(f"First: {reminders[0].crop_name}, {reminders[0].month}, {reminders[0].tip_text[:50]}")

asyncio.run(main())
