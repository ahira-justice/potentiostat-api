from app.common import utils
from app.common.data.models import User
from app.modules.user.user_dtos import UserResponse, UserCreateRequest


def user_to_user_response(user: User) -> UserResponse:
    result = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        phone_number=user.phone_number,
        first_name=user.first_name,
        last_name=user.last_name,
        is_admin=user.is_admin,
        is_staff=user.is_staff
    )

    return result


def user_create_to_user(user_create: UserCreateRequest) -> User:
    password_hash, password_salt = utils.generate_hash_and_salt(user_create.password)

    result = User(
        username=user_create.username,
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        password_hash=password_hash,
        password_salt=password_salt
    )

    return result
