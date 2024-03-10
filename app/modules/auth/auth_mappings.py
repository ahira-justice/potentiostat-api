from app.common.data.models import User
from app.modules.auth.auth_dtos import ExternalLoginRequest


def external_login_to_user(external_login: ExternalLoginRequest) -> User:
    username = external_login.email if external_login.email else external_login.phone_number

    result = User(
        username=username,
        email=external_login.email,
        phone_number=external_login.phone_number,
        fname=external_login.first_name,
        lname=external_login.last_name
    )

    return result
