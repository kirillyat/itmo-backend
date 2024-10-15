import pytest
from unittest.mock import MagicMock
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import http
from datetime import datetime
from lecture_4.demo_service.api.utils import (
    initialize,
    user_service,
    requires_author,
    requires_admin,
    value_error_handler,
)
from lecture_4.demo_service.core.users import (
    UserEntity,
    UserInfo,
    UserRole,
    password_is_longer_than_8,
    UserService,
)
from fastapi.security import HTTPBasicCredentials

# 1. Тест для функции`initialize(app)`


# @pytest.mark.asyncio
# async def test_initialize():
#     """Тест на инициализацию app с user_service."""

#     app = MagicMock()
#     initialize(app)

#     # Check that user_service is set in app.state
#     assert app.state.user_service is not None
#     assert isinstance(app.state.user_service, UserService)

#     # Check if the admin user is correctly registered
#     user_service = app.state.user_service
#     admin_user = user_service.get_by_username("admin")


def test_user_service_initialized():
    """Тест на получение user_service из request, когда он инициализирован."""

    request = MagicMock(spec=Request)
    request.app.state.user_service = MagicMock(
        spec=UserService
    )  # Инициализируем сервис

    service = user_service(request)
    assert service == request.app.state.user_service


# def test_user_service_not_initialized():
#     """Тест на случай, когда user_service не инициализирован."""

#     request = MagicMock(spec=Request)
#     request.app.state.user_service = None  # Невалидное состояние

#     with pytest.raises(AssertionError, match="User service not initialized"):
#         user_service(request)

# 3. Тесты функции `requires_author(credentials, user_service)`


@pytest.mark.asyncio
async def test_requires_author_valid():
    """Тест на успешную авторизацию пользователя."""

    credentials = HTTPBasicCredentials(username="validuser", password="validpassword")
    user_service = MagicMock()

    user_entity = UserEntity(
        uid=1,
        info=UserInfo(
            username="validuser",
            name="Valid User",
            birthdate="1990-01-01T00:00:00",
            password="validpassword",
        ),
    )

    user_service.get_by_username.return_value = user_entity

    result = requires_author(credentials, user_service)
    assert result == user_entity


@pytest.mark.asyncio
async def test_requires_author_invalid_user():
    """Тест на неуспешную авторизацию, когда пользователь не найден."""

    credentials = HTTPBasicCredentials(username="invaliduser", password="anything")
    user_service = MagicMock()

    user_service.get_by_username.return_value = None  # Пользователь не существует

    with pytest.raises(HTTPException) as exc_info:
        requires_author(credentials, user_service)


@pytest.mark.asyncio
async def test_requires_author_invalid_password():
    """Тест на неуспешную авторизацию, когда пароль неверный."""

    credentials = HTTPBasicCredentials(username="validuser", password="wrongpassword")
    user_service = MagicMock()

    user_entity = UserEntity(
        uid=1,
        info=UserInfo(
            username="validuser",
            name="Valid User",
            birthdate="1990-01-01T00:00:00",
            password="correctpassword",
        ),
    )

    user_service.get_by_username.return_value = user_entity

    with pytest.raises(HTTPException) as exc_info:
        requires_author(credentials, user_service)


# 4. Тесты функции `requires_admin(author)`


@pytest.mark.asyncio
async def test_requires_admin_valid():
    """Тест на успешное подтверждение пользователя с правами администратора."""

    admin_author = UserEntity(
        uid=1,
        info=UserInfo(
            username="adminuser",
            name="Admin User",
            birthdate="1990-01-01T00:00:00",
            password="SuperSecret123",
            role=UserRole.ADMIN,
        ),
    )

    result = requires_admin(admin_author)
    assert result == admin_author


@pytest.mark.asyncio
async def test_requires_admin_forbidden():
    """Тест на ошибку доступа `403 Forbidden`, если пользователь не является администратором."""

    non_admin_author = UserEntity(
        uid=1,
        info=UserInfo(
            username="basicuser",
            name="User",
            birthdate="1990-01-01T00:00:00",
            password="SuperSecret123",
            role=UserRole.USER,
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        requires_admin(non_admin_author)


# 5. Тесты функции `value_error_handler`


@pytest.mark.asyncio
async def test_value_error_handler():
    """Тест на корректную обработку исключения `ValueError`."""

    request = MagicMock(spec=Request)
    exc = ValueError("Test error")

    # Вызываем обработчик ошибок напрямую
    response = await value_error_handler(request, exc)

    assert response.status_code == 400  # Bad Request
