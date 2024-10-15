from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.core.users import UserInfo, UserEntity, UserRole
from lecture_4.demo_service.api.contracts import RegisterUserRequest
from requests.auth import HTTPBasicAuth

client = TestClient(create_app())


@pytest.mark.asyncio
async def test_get_user_by_id():
    """Test the /user-get endpoint by fetching user by id."""

    mock_user_service = MagicMock()
    author = MagicMock()

    # Mock return value for get_by_id
    user_entity = UserEntity(
        uid=1,
        info=UserInfo(
            username="newuser",
            name="New User",
            birthdate="1990-01-01T00:00:00",
            password="SuperSecret123",
        ),
    )
    mock_user_service.get_by_id.return_value = user_entity

    # Use Basic Auth for the author
    auth = HTTPBasicAuth("auth_user", "auth_password")
    with TestClient(create_app()) as client:
        client.app.state.user_service = mock_user_service
        response = client.post("/user-get?id=1", auth=auth)


@pytest.mark.asyncio
async def test_get_user_by_username():
    """Test the /user-get endpoint by fetching user by username."""

    mock_user_service = MagicMock()
    author = MagicMock()

    # Mock return value for get_by_username
    user_entity = UserEntity(
        uid=1,
        info=UserInfo(
            username="newuser",
            name="New User",
            birthdate="1990-01-01T00:00:00",
            password="SuperSecret123",
        ),
    )
    mock_user_service.get_by_username.return_value = user_entity

    # Use Basic Auth for the author
    auth = HTTPBasicAuth("auth_user", "auth_password")
    with TestClient(create_app()) as client:
        client.app.state.user_service = mock_user_service
        response = client.post("/user-get?username=newuser", auth=auth)


@pytest.mark.asyncio
async def test_promote_user():
    """Test the /user-promote endpoint."""

    mock_user_service = MagicMock()

    # Use Basic Auth for promoting the user
    auth = HTTPBasicAuth("admin_user", "admin_password")
    with TestClient(create_app()) as client:
        client.app.state.user_service = mock_user_service
        response = client.post("/user-promote?id=1", auth=auth)


@pytest.mark.asyncio
async def test_error_providing_both_id_and_username():
    """Test providing both id and username, which should raise an error."""

    mock_user_service = MagicMock()
    author = MagicMock()

    # Use Basic Auth for authentication
    auth = HTTPBasicAuth("auth_user", "auth_password")
    with TestClient(create_app()) as client:
        client.app.state.user_service = mock_user_service

        # This should raise an error because both id and username are provided
        response = client.post("/user-get?id=1&username=newuser", auth=auth)


@pytest.mark.asyncio
async def test_error_providing_neither_id_nor_username():
    """Test providing neither id nor username, which should raise an error."""

    mock_user_service = MagicMock()
    author = MagicMock()

    # Use Basic Auth for authentication
    auth = HTTPBasicAuth("auth_user", "auth_password")
    with TestClient(create_app()) as client:
        client.app.state.user_service = mock_user_service

        # This should raise an error because neither id nor username is provided
        response = client.post("/user-get", auth=auth)
