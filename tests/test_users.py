"""
Тесты для эндпоинтов пользователей: POST /users/register, GET /users/{telegram_username}
"""
import pytest


class TestRegisterUser:
    """Тесты регистрации пользователей"""

    def test_register_new_user(self, client):
        """Регистрация нового пользователя возвращает 201 и корректные данные"""
        response = client.post(
            "/users/register",
            json={"telegram_username": "sergey_dacha"}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["telegram_username"] == "sergey_dacha"
        assert "id" in data
        assert "created_at" in data

    def test_register_existing_user_returns_same(self, client):
        """Повторная регистрация того же пользователя возвращает существующую запись (201, но тот же ID)"""
        payload = {"telegram_username": "vasya_ogorod"}
        r1 = client.post("/users/register", json=payload)
        r2 = client.post("/users/register", json=payload)
        assert r1.status_code == 201
        # В текущей реализации всегда 201, но ID должен совпадать
        assert r1.json()["id"] == r2.json()["id"]

    def test_register_empty_username_rejected(self, client):
        """Пустой username отклоняется (422)"""
        response = client.post("/users/register", json={"telegram_username": ""})
        assert response.status_code == 422

    def test_register_no_body_rejected(self, client):
        """Отсутствие тела запроса — 422"""
        response = client.post("/users/register")
        assert response.status_code == 422


class TestGetUser:
    """Тесты получения пользователя"""

    def test_get_existing_user(self, client):
        """Получение существующего пользователя"""
        client.post("/users/register", json={"telegram_username": "masha_garden"})
        response = client.get("/users/masha_garden")
        assert response.status_code == 200
        data = response.json()
        assert data["telegram_username"] == "masha_garden"
        assert "id" in data
        assert "created_at" in data

    def test_get_nonexistent_user(self, client):
        """Запрос несуществующего пользователя — 404"""
        response = client.get("/users/who_is_this_12345")
        assert response.status_code == 404
