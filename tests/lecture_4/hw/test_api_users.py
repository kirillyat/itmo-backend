from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock
from datetime import datetime
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserEntity, UserInfo
from lecture_4.demo_service.api.contracts import RegisterUserRequest
from requests.auth import HTTPBasicAuth

client = TestClient(create_app())


# Test `/user-get` Endpoint - Fetch by `id`
@pytest.mark.asyncio
async def test_get_user_by_id():
    app = create_app()
    with TestClient(app) as client:
        app.state.user_service = MagicMock()

        # Mock `user_service.get_by_id` to return a user
        user_entity = UserEntity(
            uid=1,
            info=UserInfo(
                username="newuser",
                name="New User",
                birthdate="1990-01-01T00:00:00",
                password="SuperSecret123",
            ),
        )
        app.state.user_service.get_by_id.return_value = user_entity

        response = client.post(
            "/user-get?id=1", auth=HTTPBasicAuth("validuser", "correctpassword")
        )


# Test `/user-get` Endpoint - Fetch by `username`
@pytest.mark.asyncio
async def test_get_user_by_username():
    app = create_app()
    with TestClient(app) as client:
        app.state.user_service = MagicMock()

        # Mock `user_service.get_by_username` to return a user
        user_entity = UserEntity(
            uid=1,
            info=UserInfo(
                username="newuser",
                name="New User",
                birthdate="1990-01-01T00:00:00",
                password="SuperSecret123",
            ),
        )
        app.state.user_service.get_by_username.return_value = user_entity

        response = client.post(
            "/user-get?username=newuser",
            auth=HTTPBasicAuth("validuser", "correctpassword"),
        )


# Test `/user-get` Endpoint - Error: Both `id` and `username` provided
@pytest.mark.asyncio
async def test_error_both_id_and_username():
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/user-get?id=1&username=newuser",
            auth=HTTPBasicAuth("validuser", "correctpassword"),
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


# Test `/user-get` Endpoint - Error: Neither `id` nor `username` provided
@pytest.mark.asyncio
async def test_error_neither_id_nor_username():
    app = create_app()
    with TestClient(app) as client:
        response = client.post(
            "/user-get", auth=HTTPBasicAuth("validuser", "correctpassword")
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


# Test `/user-promote` Endpoint
@pytest.mark.asyncio
async def test_promote_user():
    app = create_app()
    with TestClient(app) as client:
        app.state.user_service = MagicMock()

        response = client.post(
            "/user-promote?id=1", auth=HTTPBasicAuth("adminuser", "adminpassword")
        )
