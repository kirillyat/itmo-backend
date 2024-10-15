from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock
from datetime import datetime
from fastapi import HTTPException
from lecture_4.demo_service.api.main import create_app
from lecture_4.demo_service.api.contracts import RegisterUserRequest
from lecture_4.demo_service.core.users import UserInfo, UserEntity, UserRole
from requests.auth import HTTPBasicAuth


client = TestClient(create_app())

# Test `/user-register` Endpoint


# @pytest.mark.asyncio
# async def test_register_user():
#     """Test the /user-register endpoint for registering a user."""
#     body = RegisterUserRequest(
#         username="newuser",
#         name="New User",
#         birthdate="1990-01-01T00:00:00",
#         password="SuperSecret123",
#     )

#     # Mock data
#     user_info = UserInfo(**body.model_dump())
#     user_entity = UserEntity(uid=1, info=user_info)

#     # Mock the UserService
#     with TestClient(create_app()) as client:
#         response = client.post("/user-register", json=body.model_dump())


@pytest.mark.asyncio
async def test_get_user_by_username():
    """Test the /user-get endpoint for fetching user by username."""

    app = create_app()
    with TestClient(app) as client:
        # Mock UserService in application state
        app.state.user_service = MagicMock()

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

        response = client.post("/user-get?username=newuser")


# Test `/user-promote` Endpoint


@pytest.mark.asyncio
async def test_promote_user():
    """Test the /user-promote endpoint for promoting a user to admin."""

    app = create_app()
    with TestClient(app) as client:
        app.state.user_service = MagicMock()

        response = client.post(
            "/user-promote?id=1", auth=HTTPBasicAuth("adminuser", "adminpassword")
        )


# Test that neither `id` nor `username` is provided in `/user-get`


@pytest.mark.asyncio
async def test_error_missing_id_and_username():
    """Test the /user-get endpoint where both id and username are missing."""

    app = create_app()
    with TestClient(app) as client:
        # Call endpoint without id and username, which should raise a ValueError
        response = client.post("/user-get")

        assert response.status_code == 401


# Test utility functions (`requires_author`, `requires_admin`, `user_service`, and more)


@pytest.mark.asyncio
async def test_requires_author_valid():
    """Test requires_author with valid credentials."""

    from fastapi.security import HTTPBasicCredentials
    from lecture_4.demo_service.api.utils import requires_author
    from lecture_4.demo_service.core.users import UserInfo, UserEntity

    credentials = HTTPBasicCredentials(username="newuser", password="correctPassword")
    mock_user_service = MagicMock()

    # Mock user entity with matching credentials
    user_entity = UserEntity(
        uid=1,
        info=UserInfo(
            username="newuser",
            name="New User",
            birthdate="1990-01-01T00:00:00",
            password="correctPassword",
        ),
    )

    # Mock `get_by_username` method to return an existing user
    mock_user_service.get_by_username.return_value = user_entity

    # Simulate the correct authorization for valid credentials
    author = requires_author(credentials, mock_user_service)
    assert author == user_entity


@pytest.mark.asyncio
async def test_requires_author_invalid():
    """Test requires_author when credentials are invalid."""

    from fastapi.security import HTTPBasicCredentials
    from lecture_4.demo_service.api.utils import requires_author

    credentials = HTTPBasicCredentials(username="fakeuser", password="wrongPassword")
    mock_user_service = MagicMock()

    # Mock user service to return None (invalid user)
    mock_user_service.get_by_username.return_value = None

    # Expecting an HTTPException for invalid credentials
    with pytest.raises(HTTPException) as exc_info:
        requires_author(credentials, mock_user_service)

    assert exc_info.value.status_code == 401  # 401 Unauthorized


@pytest.mark.asyncio
async def test_requires_admin_valid():
    """Test requires_admin where user is an admin."""

    from lecture_4.demo_service.api.utils import requires_admin
    from lecture_4.demo_service.core.users import UserInfo, UserEntity, UserRole

    # Admin role user
    admin_user = UserEntity(
        uid=1,
        info=UserInfo(
            username="adminuser",
            name="Admin User",
            birthdate="1990-01-01T00:00:00",
            password="SuperSecret123",
            role=UserRole.ADMIN,
        ),
    )

    # Ensure requires_admin returns the user without exception
    returned_user = requires_admin(admin_user)
    assert returned_user == admin_user


@pytest.mark.asyncio
async def test_requires_admin_forbidden():
    """Test requires_admin raises a 403 error for non-admin users."""

    from lecture_4.demo_service.api.utils import requires_admin
    from lecture_4.demo_service.core.users import UserInfo, UserEntity, UserRole

    # Non-admin user
    non_admin_user = UserEntity(
        uid=1,
        info=UserInfo(
            username="basicuser",
            name="User",
            birthdate="1990-01-01T00:00:00",
            password="SuperSecret123",
            role=UserRole.USER,
        ),
    )

    # Expecting a 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        requires_admin(non_admin_user)

    assert exc_info.value.status_code == 403  # Forbidden
