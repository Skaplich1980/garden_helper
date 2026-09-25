# bot/handlers/user.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
import logging

from bot.services.api_client import api_client

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Обработка команды /start.
    Мы используем async def, потому что внутри делаем await-запрос к API.
    """
    username = message.from_user.username or f"user_{message.from_user.id}"

    try:
        # Асинхронно регистрируем пользователя в нашем API
        user_data = await api_client.register_user(username)
        logger.info(f"Пользователь {username} успешно зарегистрирован/найден (ID: {user_data['id']})")

        await message.answer(
            f"Привет, {message.from_user.full_name}!\n\n"
            f"Я твой Огородный Помощник\n"
            f"Я помогу тебе управлять задачами на твоих 25 сотках.\n\n"
            f"Доступные команды:\n"
            f"/tasks - показать мои активные задачи\n"
            f"/help - получить сезонную памятку\n"
            f"/add - добавить новую задачу"
        )
    except Exception as e:
        logger.error(f"Не удалось обработать команду /start для {username}: {e}")
        await message.answer("Ошибка при подключении к серверу. Попробуйте позже.")


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    """Показывает список активных задач пользователя"""
    username = message.from_user.username or f"user_{message.from_user.id}"

    await message.answer("Загружаю ваши задачи...")

    # Асинхронно запрашиваем задачи с бэкенда.
    # Пока идет запрос, event loop может обрабатывать другие сообщения от других пользователей!
    tasks = await api_client.get_tasks(username, completed=False)

    if not tasks:
        await message.answer("У вас пока нет активных задач. Отличная работа!")
        return

    text = "Ваши активные задачи:\n\n"
    for task in tasks:
        due = f" (до {task['due_date']})" if task['due_date'] else ""
        text += f"#{task['id']}. {task['title']}{due}\n"
        if task['description']:
            text += f"   {task['description']}\n"
        text += "\n"

    text += "Чтобы отметить задачу выполненной, используйте команду:\n/done <ID_задачи>\n(например: `/done 1`)"

    await message.answer(text, parse_mode="Markdown")


@router.message(Command("done"))
async def cmd_done(message: Message):
    """Отмечает задачу выполненной по ID"""
    # Извлекаем аргумент команды (например, из "/done 1" получим "1")
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Пожалуйста, укажите ID задачи. Пример: `/done 1`", parse_mode="Markdown")
        return

    task_id_str = args[1]
    if not task_id_str.isdigit():
        await message.answer("ID задачи должен быть числом.", parse_mode="Markdown")
        return

    task_id = int(task_id_str)

    await message.answer(f"Отмечаю задачу #{task_id} как выполненную...")

    updated_task = await api_client.complete_task(task_id)

    if updated_task:
        await message.answer(
            f"Отлично! Задача \"{updated_task['title']}\" отмечена как выполненная. Так держать!",
            parse_mode="Markdown")
    else:
        await message.answer(f"Не удалось найти задачу с ID {task_id} или обновить её статус.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Показывает сезонную памятку для ТЕКУЩЕГО месяца.
    Делает асинхронный запрос к API, получая актуальные советы из БД.
    """
    from datetime import datetime
    
    # Определяем текущий месяц
    current_month = datetime.now().month
    month_names = [
        "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    month_name = month_names[current_month]
    
    await message.answer(f"Загружаю памятку на {month_name.lower()}...")
    
    # Асинхронно запрашиваем рекомендации из API
    # Пока идёт запрос, event loop свободен для других пользователей
    reminders = await api_client.get_reminders(current_month)
    
    if not reminders:
        await message.answer(
            f" На {month_name} пока нет рекомендаций.\n"
            f"Попробуйте позже — мы постоянно обновляем базу знаний!"
        )
        return
    
    # Формируем красивое сообщение
    text = f"Сезонная памятка ({month_name}):\n\n"
    
    for reminder in reminders:
        crop = reminder["crop_name"]
        tip = reminder["tip_text"]
        # Определяем эмодзи по культуре
        emoji = {
            "Томаты": "🍅", "Картофель": "🥔", "Огурцы": "🥒",
            "Морковь": "🥕", "Капуста": "🥬", "Перец": "🌶️",
            "Баклажаны": "🍆", "Озимый чеснок": "🧄",
            "Мотоблок": "🚜", "Полив": "💧", "Теплица": "🏠",
            "Общее": "📋"
        }.get(crop, "🌱")
        
        text += f"{emoji} **{crop}:** {tip}\n\n"
    
    text += f"_Советов на этот месяц: {len(reminders)}_"
    
    await message.answer(text, parse_mode="Markdown")


@router.message(Command("add"))
async def cmd_add(message: Message):
    """
    Создание новой задачи.
    Формат: /add <название> | <описание> | <тип>
    Типы: planting, watering, motoblock, harvest, general
    
    Примеры:
    /add Полить томаты | Обильный полив под корень | watering
    /add Вспахать огород | Мотоблоком весь участок | motoblock
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "Укажите параметры задачи.\n\n"
            "**Формат:** `/add Название | Описание | тип`\n\n"
            "**Типы задач:**\n"
            "- planting - посадка\n"
            "- watering - полив\n"
            "- motoblock - мотоблок\n"
            "- harvest - сбор урожая\n"
            "- general - общее (по умолчанию)\n\n"
            "**Пример:**\n"
            "`/add Полить томаты | Обильный полив под корень | watering`",
            parse_mode="Markdown"
        )
        return
    
    # Парсим аргументы
    parts = args[1].split("|")
    title = parts[0].strip()
    description = parts[1].strip() if len(parts) > 1 else None
    task_type = parts[2].strip() if len(parts) > 2 else "general"
    
    # Валидация типа задачи
    valid_types = {"planting", "watering", "motoblock", "harvest", "general"}
    if task_type not in valid_types:
        await message.answer(
            f"Неизвестный тип задачи: `{task_type}`\n"
            f"Допустимые: {', '.join(sorted(valid_types))}",
            parse_mode="Markdown"
        )
        return
    
    username = message.from_user.username or f"user_{message.from_user.id}"
    
    await message.answer("Создаю задачу...")
    
    new_task = await api_client.create_task(
        telegram_username=username,
        title=title,
        description=description,
        task_type=task_type
    )
    
    if new_task:
        type_emoji = {
            "planting": "🌱", "watering": "💧", 
            "motoblock": "🚜", "harvest": "", "general": "📋"
        }.get(task_type, "📋")
        
        await message.answer(
            f"Задача создана!\n\n"
            f"{type_emoji} *#{new_task['id']}. {new_task['title']}*\n"
            f"Тип: `{new_task['task_type']}`\n"
            f"Статус: В работе\n\n"
            f"Чтобы отметить выполненной: `/done {new_task['id']}`",
            parse_mode="Markdown"
        )
    else:
        await message.answer("Не удалось создать задачу. Попробуйте позже.")
