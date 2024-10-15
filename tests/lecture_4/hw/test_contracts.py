from datetime import datetime
from pydantic import SecretStr
from lecture_4.demo_service.api.contracts import RegisterUserRequest, UserResponse
from lecture_4.demo_service.core.users import UserEntity, UserRole, UserInfo


def test_register_user_request_creation():
    user_request = RegisterUserRequest(
        username="janedoe",
        name="Jane Doe",
        birthdate=datetime(1990, 1, 1),
        password=SecretStr("SuperSecret123"),
    )

    assert user_request.username == "janedoe"
    assert user_request.name == "Jane Doe"
    assert user_request.birthdate == datetime(1990, 1, 1)


def test_user_response_from_entity():
    user_info = UserInfo(
        username="janedoe",
        name="Jane Doe",
        birthdate=datetime(1990, 1, 1),
        password=SecretStr("SuperSecret123"),
        role=UserRole.USER,
    )
    user_entity = UserEntity(uid=1, info=user_info)

    response = UserResponse.from_user_entity(user_entity)

    assert response.uid == 1
    assert response.username == "janedoe"
    assert response.name == "Jane Doe"
    assert response.birthdate == datetime(1990, 1, 1)
    assert response.role == UserRole.USER
