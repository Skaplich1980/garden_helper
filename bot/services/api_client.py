# bot/services/api_client.py
import httpx
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
logger = logging.getLogger(__name__)

class APIClient:
    """
    Асинхронный клиент для взаимодействия с FastAPI Backend.
    Используем один экземпляр AsyncClient на все время жизни бота (best practice для httpx).
    """
    def __init__(self):
        # timeout=10.0 гарантирует, что запрос не будет висеть бесконечно
        self.client = httpx.AsyncClient(base_url=API_URL, timeout=10.0)

    async def close(self):
        """Корректное закрытие клиента при остановке бота"""
        await self.client.aclose()

    async def register_user(self, telegram_username: str) -> Dict[str, Any]:
        """Регистрирует или получает пользователя по username"""
        try:
            response = await self.client.post(
                "/users/register",
                json={"telegram_username": telegram_username}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Ошибка при регистрации пользователя {telegram_username}: {e}")
            raise

    async def get_tasks(self, telegram_username: str, completed: bool = False) -> List[Dict[str, Any]]:
        """Получает список задач пользователя"""
        try:
            response = await self.client.get(
                "/tasks/",
                params={"telegram_username": telegram_username, "completed": completed}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Ошибка при получении задач для {telegram_username}: {e}")
            return []

    async def complete_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Отмечает задачу как выполненную (PATCH запрос)"""
        try:
            response = await self.client.patch(
                f"/tasks/{task_id}",
                json={"is_completed": True}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Ошибка при обновлении задачи {task_id}: {e}")
            return None

    async def get_reminders(self, month: int) -> List[Dict[str, Any]]:
        """Получает сезонные рекомендации для указанного месяца"""
        try:
            response = await self.client.get(
                "/reminders/",
                params={"month": month}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Ошибка при получении рекомендаций для месяца {month}: {e}")
            return []

    async def create_task(
        self, 
        telegram_username: str, 
        title: str, 
        description: str | None = None,
        task_type: str = "general"
    ) -> Optional[Dict[str, Any]]:
        """Создаёт новую задачу через API"""
        try:
            payload = {
                "telegram_username": telegram_username,
                "title": title,
                "description": description,
                "task_type": task_type
            }
            response = await self.client.post("/tasks/", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Ошибка при создании задачи для {telegram_username}: {e}")
            return None

# Создаем глобальный экземпляр клиента, который будем использовать в хендлерах
api_client = APIClient()
