import pytest
from datetime import datetime
from pydantic import SecretStr
from lecture_4.demo_service.core.users import (
    UserInfo,
    UserService,
    UserRole,
    password_is_longer_than_8,
)


@pytest.fixture
def user_info():
    """Fixture to create sample user info."""
    return UserInfo(
        username="testuser",
        name="Test User",
        birthdate=datetime.now(),
        password=SecretStr("SuperSecret123"),
    )


@pytest.fixture
def user_service():
    """Fixture to create UserService instance."""
    return UserService(password_validators=[password_is_longer_than_8])


def test_password_is_longer_than_8():
    """Test the password length validator."""
    assert password_is_longer_than_8("short") is False
    assert password_is_longer_than_8("longenoughpassword") is True


def test_register_user_success(user_service, user_info):
    """Test successful registration of a new user."""
    user_entity = user_service.register(user_info)
    assert user_entity.info.username == "testuser"
    assert user_entity.info.role == UserRole.USER
    assert user_entity.info.password.get_secret_value() == "SuperSecret123"


def test_register_user_duplicate_username(user_service, user_info):
    """Test trying to register a user with a duplicate username."""
    # Register the user with the username "testuser"
    user_service.register(user_info)

    # Try to register the user again with the same username
    with pytest.raises(ValueError, match="username is already taken"):
        user_service.register(user_info)


def test_register_user_invalid_password(user_service, user_info):
    """Test registering a user with an invalid password."""
    user_service.password_validators = [
        lambda pwd: len(pwd) > 15
    ]  # Password must be longer than 15 characters

    user_info.password = SecretStr("shortpass")

    with pytest.raises(ValueError, match="invalid password"):
        user_service.register(user_info)


def test_get_user_by_username_success(user_service, user_info):
    """Test retrieving a user by their username."""
    user_entity = user_service.register(user_info)

    found_user = user_service.get_by_username("testuser")
    assert found_user == user_entity


def test_get_user_by_username_not_found(user_service):
    """Test retrieving a user by username when the user doesn't exist."""
    found_user = user_service.get_by_username("unknownuser")
    assert found_user is None


def test_get_user_by_id_success(user_service, user_info):
    """Test retrieving a user by their ID."""
    user_entity = user_service.register(user_info)

    found_user = user_service.get_by_id(user_entity.uid)
    assert found_user == user_entity


def test_get_user_by_id_not_found(user_service):
    """Test retrieving a user by ID when the user doesn't exist."""
    found_user = user_service.get_by_id(999)
    assert found_user is None


def test_grant_admin_role(user_service, user_info):
    """Test granting a user admin privileges."""
    user_entity = user_service.register(user_info)

    user_service.grant_admin(user_entity.uid)
    assert user_entity.info.role == UserRole.ADMIN
