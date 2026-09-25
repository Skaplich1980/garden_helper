"""
Тесты для эндпоинтов задач: POST /tasks, GET /tasks, PATCH /tasks/{id}, DELETE /tasks/{id}
"""
import pytest


@pytest.fixture
def user(client):
    """Создаём тестового пользователя для всех тестов задач"""
    response = client.post("/users/register", json={"telegram_username": "test_gardener"})
    assert response.status_code == 201
    return response.json()


class TestCreateTask:
    """Тесты создания задачи"""

    def test_create_task_success(self, client, user):
        """Создание задачи возвращает 201 и полный объект задачи"""
        response = client.post("/tasks/", json={
            "telegram_username": "test_gardener",
            "title": "Посадить помидоры",
            "description": "Высадить рассаду в теплицу",
            "due_date": "2026-06-15",
            "task_type": "planting"
        })
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["title"] == "Посадить помидоры"
        assert data["description"] == "Высадить рассаду в теплицу"
        assert data["task_type"] == "planting"
        assert data["is_completed"] is False
        assert data["user_id"] == user["id"]

    def test_create_task_defaults(self, client, user):
        """Создание задачи без optional-полей: description и due_date должны быть null,
        task_type — 'general'"""
        response = client.post("/tasks/", json={
            "telegram_username": "test_gardener",
            "title": "Полить грядки"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["description"] is None
        assert data["due_date"] is None
        assert data["task_type"] == "general"
        assert data["is_completed"] is False

    def test_create_task_without_user(self, client):
        """Создание задачи для несуществующего пользователя — 404"""
        response = client.post("/tasks/", json={
            "telegram_username": "nobody",
            "title": "Невозможно создать"
        })
        assert response.status_code == 404

    def test_create_task_empty_title_rejected(self, client, user):
        """Заголовок не может быть пустым — 422"""
        response = client.post("/tasks/", json={
            "telegram_username": "test_gardener",
            "title": ""
        })
        assert response.status_code == 422

    def test_create_task_no_body_rejected(self, client, user):
        """Отсутствие тела — 422"""
        response = client.post("/tasks/")
        assert response.status_code == 422


class TestGetUserTasks:
    """Тесты получения списка задач"""

    def _create_tasks(self, client, user):
        """Вспомогательная функция: создаёт несколько задач"""
        client.post("/tasks/", json={
            "telegram_username": user["telegram_username"],
            "title": "Посадить картофель",
            "task_type": "planting"
        })
        client.post("/tasks/", json={
            "telegram_username": user["telegram_username"],
            "title": "Полить огурцы",
            "task_type": "watering"
        })
        client.post("/tasks/", json={
            "telegram_username": user["telegram_username"],
            "title": "Обработать мотоблоком",
            "task_type": "motoblock"
        })

    def test_get_tasks_empty(self, client, user):
        """У пользователя без задач — пустой массив"""
        response = client.get("/tasks/", params={
            "telegram_username": user["telegram_username"]
        })
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tasks_returns_all(self, client, user):
        """Возвращает все задачи пользователя"""
        self._create_tasks(client, user)
        response = client.get("/tasks/", params={
            "telegram_username": user["telegram_username"]
        })
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3

    def test_get_tasks_filter_completed_false(self, client, user):
        """Фильтр completed=False — только невыполненные"""
        self._create_tasks(client, user)
        response = client.get("/tasks/", params={
            "telegram_username": user["telegram_username"],
            "completed": False
        })
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        assert all(t["is_completed"] is False for t in tasks)

    def test_get_tasks_filter_completed_true(self, client, user):
        """Фильтр completed=True — только выполненные (их пока нет)"""
        self._create_tasks(client, user)
        response = client.get("/tasks/", params={
            "telegram_username": user["telegram_username"],
            "completed": True
        })
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tasks_nonexistent_user(self, client):
        """Запрос задач несуществующего пользователя — 404"""
        response = client.get("/tasks/", params={"telegram_username": "ghost"})
        assert response.status_code == 404


class TestUpdateTask:
    """Тесты обновления задачи (PATCH)"""

    def _create_and_update(self, client):
        """Создаём задачу и возвращаем её ID"""
        r = client.post("/tasks/", json={
            "telegram_username": "test_gardener",
            "title": "Изначальный заголовок",
            "description": "Старое описание"
        })
        assert r.status_code == 201
        return r.json()["id"]

    def test_update_task_mark_completed(self, client, user):
        """Отметка задачи как выполненной"""
        task_id = self._create_and_update(client)
        response = client.patch(f"/tasks/{task_id}", json={"is_completed": True})
        assert response.status_code == 200
        data = response.json()
        assert data["is_completed"] is True
        # title и description не должны измениться
        assert data["title"] == "Изначальный заголовок"

    def test_update_task_title_only(self, client, user):
        """Обновление только заголовка (description остаётся прежним)"""
        task_id = self._create_and_update(client)
        response = client.patch(f"/tasks/{task_id}", json={"title": "Новый заголовок"})
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Новый заголовок"
        assert data["description"] == "Старое описание"

    def test_update_nonexistent_task(self, client):
        """Обновление несуществующей задачи — 404"""
        response = client.patch("/tasks/99999", json={"is_completed": True})
        assert response.status_code == 404

    def test_update_empty_body(self, client, user):
        """Пустой body — задача не меняется, 200 (ничего не обновляем)"""
        task_id = self._create_and_update(client)
        response = client.patch(f"/tasks/{task_id}", json={})
        assert response.status_code == 200


class TestDeleteTask:
    """Тесты удаления задачи"""

    def test_delete_existing_task(self, client, user):
        """Удаление существующей задачи — 204"""
        r = client.post("/tasks/", json={
            "telegram_username": "test_gardener",
            "title": "Удаляемая задача"
        })
        task_id = r.json()["id"]

        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 204

        # Убедимся, что задача действительно удалена
        response = client.get("/tasks/", params={
            "telegram_username": user["telegram_username"]
        })
        tasks = response.json()
        assert all(t["id"] != task_id for t in tasks)

    def test_delete_nonexistent_task(self, client):
        """Удаление несуществующей задачи — 404"""
        response = client.delete("/tasks/99999")
        assert response.status_code == 404


class TestRootEndpoint:
    """Тест корневой точки API"""

    def test_root(self, client):
        """Проверка доступности API"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Garden Helper API is running"
        assert "/docs" in data["docs_url"]
