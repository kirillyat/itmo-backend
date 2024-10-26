import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from datetime import datetime
from lecture_4.demo_service.api.users import register_user, get_user, promote_user
from lecture_4.demo_service.core.users import UserInfo, UserEntity, UserRole
from lecture_4.demo_service.api.contracts import RegisterUserRequest
from unittest.mock import MagicMock


# 1. Тест для функции "register_user"
@pytest.mark.asyncio
async def test_register_user_success():
    """Тестирование успешной регистрации пользователя."""

    user_service = MagicMock()

    # Создаем фиктивные данные на основе Pydantic-модели
    body = RegisterUserRequest(
        username="newuser",
        name="New User",
        birthdate="1990-01-01T00:00:00",
        password="SuperSecret123",
    )

    # Мокаем `UserInfo` и `UserEntity`
    user_info = UserInfo(**body.model_dump())
    user_entity = UserEntity(uid=1, info=user_info)
    user_service.register.return_value = user_entity

    # Вызываем функцию
    result = await register_user(body, user_service)

    # Проверка правильности ответа
    assert result.uid == 1
    assert result.username == "newuser"
    assert result.name == "New User"


@pytest.mark.asyncio
async def test_register_user_duplicate_username():
    """Тестирование ошибки при регистрации с дублирующимся username."""

    user_service = MagicMock()

    # Дублирующийся username
    body = RegisterUserRequest(
        username="duplicateuser",
        name="Duplicate User",
        birthdate="1990-01-01T00:00:00",
        password="SuperSecret123",
    )

    # Указываем, что мокаем ошибку в UserService
    user_service.register.side_effect = ValueError("username is already taken")

    # Ожидаем поднятие исключения ValueError
    with pytest.raises(ValueError, match="username is already taken"):
        await register_user(body, user_service)


# 2. Тесты для функции "get_user"
@pytest.mark.asyncio
async def test_get_user_by_id_success():
    """Тестирование успешного получения пользователя по ID."""

    user_service = MagicMock()
    author = MagicMock()

    user_entity = UserEntity(
        uid=1,
        info=UserInfo(
            username="newuser",
            name="New User",
            birthdate=datetime.now(),
            password="SuperSecret123",
        ),
    )

    # Мокаем возврат пользователя через user_service.get_by_id
    user_service.get_by_id.return_value = user_entity
    author.uid = 1  # Авторизация пользователя

    # Вызываем функцию напрямую
    result = await get_user(user_service=user_service, author=author, id=1)

    # Проверка результата
    assert result.uid == 1
    assert result.username == "newuser"


@pytest.mark.asyncio
async def test_get_user_by_username_success():
    """Тестирование успешного получения пользователя по username."""

    user_service = MagicMock()
    author = MagicMock()

    user_entity = UserEntity(
        uid=1,
        info=UserInfo(
            username="newuser",
            name="New User",
            birthdate=datetime.now(),
            password="SuperSecret123",
        ),
    )

    # Мокаем вызов user_service.get_by_username
    user_service.get_by_username.return_value = user_entity
    author.info.username = "newuser"  # Авторизация через автор

    # Вызываем функцию напрямую с username
    result = await get_user(
        user_service=user_service, author=author, username="newuser"
    )

    # Проверка возвращенного результата
    assert result.uid == 1
    assert result.username == "newuser"


@pytest.mark.asyncio
async def test_get_user_both_id_and_username_error():
    """Тестирование ошибки: когда переданы и id, и username."""

    user_service = MagicMock()
    author = MagicMock()

    # Ожидаем исключение ValueError
    with pytest.raises(ValueError, match="both id and username are provided"):
        await get_user(
            user_service=user_service, author=author, id=1, username="newuser"
        )


@pytest.mark.asyncio
async def test_get_user_no_id_or_username_error():
    """Тестирование ошибки: когда не переданы ни id, ни username."""

    user_service = MagicMock()
    author = MagicMock()

    # Ожидаем исключение ValueError
    with pytest.raises(ValueError, match="neither id nor username are provided"):
        await get_user(user_service=user_service, author=author)


@pytest.mark.asyncio
async def test_get_user_not_found():
    """Тестирование ошибки 404 Not Found: пользователь не найден."""

    user_service = MagicMock()
    author = MagicMock()

    # Вижем, что пользователь не найден через user_service
    user_service.get_by_id.return_value = None
    author.uid = 1

    # Ожидаем HTTPException со статусом 404 (Not Found)
    with pytest.raises(HTTPException) as exc_info:
        await get_user(user_service=user_service, author=author, id=1)

    assert exc_info.value.status_code == 404


# 3. Тест для функции "promote_user"
@pytest.mark.asyncio
async def test_promote_user_success():
    """Тестирование успешного повышения пользователя до admin."""

    user_service = MagicMock()
    admin_dep = MagicMock()  # Мок для AdminDep

    # Вызываем напрямую функцию
    await promote_user(id=1, _=admin_dep, user_service=user_service)

    # Проверяем, что user_service.grant_admin был вызван один раз
    user_service.grant_admin.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_promote_user_error_user_not_found():
    """Тестирование ошибки, когда пользователь не найден для повышения до admin."""

    user_service = MagicMock()

    # Мокаем ошибку для несуществующего пользователя
    user_service.grant_admin.side_effect = ValueError("user not found")

    # Проверка на возникновение исключения
    with pytest.raises(ValueError, match="user not found"):
        await promote_user(id=999, _=MagicMock(), user_service=user_service)
