# -*- coding: utf-8 -*-
"""
Скрипт заполнения таблицы crop_reminders тестовыми данными.
Запуск: python -m database.seed_reminders
"""
import asyncio
from database.engine import async_session_maker
from database.models import CropReminder

# База знаний агронома — 12 месяцев × несколько культур
REMINDERS_DATA = [
    {"crop_name": "Общее", "month": 1, "tip_text": "Составьте план посадок на сезон. Закажите семена. Проверьте инвентарь."},
    {"crop_name": "Теплица", "month": 1, "tip_text": "Проверьте укрытие теплицы на предмет повреждений от снега."},
    {"crop_name": "Перец", "month": 2, "tip_text": "Пора сеять перец на рассаду. Глубина заделки — 1 см."},
    {"crop_name": "Баклажаны", "month": 2, "tip_text": "Сейте баклажаны в конце февраля. Они долго всходят (до 14 дней)."},
    {"crop_name": "Томаты", "month": 3, "tip_text": "Сейте томаты на рассаду в середине марта. Пикировка через 2 недели."},
    {"crop_name": "Капуста", "month": 3, "tip_text": "Раннюю капусту — на рассаду в конце марта."},
    {"crop_name": "Мотоблок", "month": 4, "tip_text": "Первая вспашка участка после схода снега. Проверьте масло и свечи."},
    {"crop_name": "Морковь", "month": 4, "tip_text": "Можно сеять морковь под плёнку, когда почва прогреется до +5°C."},
    {"crop_name": "Томаты", "month": 5, "tip_text": "Высадка рассады томатов в теплицу после 10 мая (под укрытие)."},
    {"crop_name": "Картофель", "month": 5, "tip_text": "Посадка картофеля. Глубина — 8-10 см, расстояние между рядами — 70 см."},
    {"crop_name": "Огурцы", "month": 5, "tip_text": "В конце мая — посев огурцов в теплицу или под временное укрытие."},
    {"crop_name": "Полив", "month": 6, "tip_text": "Установите режим полива: утром или вечером, не в жару. Норма — 10 л/м2."},
    {"crop_name": "Томаты", "month": 6, "tip_text": "Начинайте пасынкование томатов раз в 7-10 дней."},
    {"crop_name": "Мотоблок", "month": 7, "tip_text": "Междурядная обработка картофеля мотоблоком — последнее окучивание."},
    {"crop_name": "Огурцы", "month": 7, "tip_text": "Собирайте огурцы ежедневно — это стимулирует новое плодоношение."},
    {"crop_name": "Томаты", "month": 8, "tip_text": "Удаляйте нижние листья и пасынки для лучшего проветривания."},
    {"crop_name": "Картофель", "month": 8, "tip_text": "Если ботва пожелтела — можно начинать выборочную копку."},
    {"crop_name": "Мотоблок", "month": 8, "tip_text": "После вспашки очистите фрезы от грязи и проверьте уровень масла."},
    {"crop_name": "Томаты", "month": 9, "tip_text": "Снимайте плоды до первых заморозков. Зелёные — на дозаривание."},
    {"crop_name": "Картофель", "month": 9, "tip_text": "Завершите уборку картофеля до середины месяца."},
    {"crop_name": "Озимый чеснок", "month": 9, "tip_text": "Подготовьте грядки для озимого чеснока. Лучшее время посадки — конец сентября."},
    {"crop_name": "Мотоблок", "month": 9, "tip_text": "Осеннее ТО мотоблока: замена масла, очистка, хранение в сухом месте."},
    {"crop_name": "Общее", "month": 10, "tip_text": "Уборка участка: сжигание ботвы, перекопка, внесение удобрений."},
    {"crop_name": "Теплица", "month": 10, "tip_text": "Дезинфекция теплицы: промойте каркас, замените верхний слой почвы (5-10 см)."},
    {"crop_name": "Общее", "month": 11, "tip_text": "Консервация инвентаря. Хранение семян в сухом прохладном месте."},
    {"crop_name": "Общее", "month": 12, "tip_text": "Анализ сезона: что получилось, что нет. Планирование следующего года."},
]


async def seed_reminders():
    """Асинхронное заполнение таблицы рекомендациями"""
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(CropReminder))
        existing = result.scalars().all()
        
        if existing:
            print(f"WARNING: Table already has {len(existing)} records. Skipping seeding.")
            return
        
        for data in REMINDERS_DATA:
            reminder = CropReminder(**data)
            session.add(reminder)
        
        await session.commit()
        print(f"Added {len(REMINDERS_DATA)} seasonal reminders.")


if __name__ == "__main__":
    asyncio.run(seed_reminders())
