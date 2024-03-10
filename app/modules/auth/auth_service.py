import hashlib
import string
import time
from datetime import datetime, timedelta

import jwt
from sqlalchemy.orm.session import Session

from app.common import utils
from app.common.data.enums import UserTokenType
from app.common.domain.config import USER_TOKEN_RESET_PASSWORD_EXPIRE_MINUTES, USER_TOKEN_RESET_PASSWORD_LENGTH, \
    ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SIGNING_ALGORITHM, SECRET_KEY
from app.common.domain.constants import FORGOT_PASSWORD_TEMPLATE
from app.common.exceptions.app_exceptions import UnauthorizedRequestException, NotFoundException
from app.modules.auth.auth_dtos import ForgotPasswordRequest, PasswordDto, ResetPasswordRequest, LoginRequest, \
    AccessTokenResponse, ExternalLoginRequest
from app.modules.email import email_service
from app.modules.user import user_service
from app.modules.user.user_dtos import UserResponse
from app.modules.user.user_mappings import user_to_user_response
from app.modules.user_token import user_token_service


def get_user_password(db: Session, username: str) -> PasswordDto:
    user = user_service.get_user_by_username(db, username)

    response = PasswordDto(
        password_hash=user.password_hash,
        password_salt=user.password_salt
    )

    return response


def verify_password(password, password_hash, password_salt) -> bool:
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        password_salt,
        100000,
        dklen=128
    )

    return key == password_hash


def authenticate_user(db: Session, username: str, password: str) -> bool:
    user_password = get_user_password(db, username)

    if not user_password:
        return False

    if not verify_password(password, user_password.password_hash, user_password.password_salt):
        return False

    return True


def forgot_password(db: Session, forgot_password_data: ForgotPasswordRequest) -> None:
    user = user_service.get_user_by_username(db, forgot_password_data.username)

    user_token = user_token_service.generate_token(
        db,
        USER_TOKEN_RESET_PASSWORD_LENGTH,
        string.ascii_letters,
        USER_TOKEN_RESET_PASSWORD_EXPIRE_MINUTES,
        UserTokenType.RESET_PASSWORD,
        user.id
    )

    payload = {
        "token": user_token.token
    }

    email_service.send_email(user.email, FORGOT_PASSWORD_TEMPLATE, payload)


def reset_password(db: Session, reset_password_data: ResetPasswordRequest) -> UserResponse:
    user = user_service.get_user_by_username(db, reset_password_data.username)

    user_token_service.use_token(db, user.id, reset_password_data.token, UserTokenType.RESET_PASSWORD)

    password_hash, password_salt = utils.generate_hash_and_salt(reset_password_data.password)

    user.password_hash = password_hash
    user.password_salt = password_salt

    db.commit()
    db.refresh(user)

    return user_to_user_response(user)


def get_access_token(db: Session, login_data: LoginRequest) -> AccessTokenResponse:
    if not authenticate_user(db, login_data.username, login_data.password):
        raise UnauthorizedRequestException("Incorrect username or password")

    expire = get_expiry(login_data.expires)

    data = {"sub": login_data.username, "exp": expire}
    return generate_access_token(data)


def get_access_token_for_external_login(db: Session, external_login_data: ExternalLoginRequest) -> AccessTokenResponse:
    username = external_login_data.email if external_login_data.email else external_login_data.phone_number

    try:
        user_service.get_user_by_username(db, username)
    except NotFoundException:
        user_service.create_social_user(db, external_login_data)

    expire = get_expiry(external_login_data.expires)

    data = {"sub": username, "exp": expire}
    return generate_access_token(data)


def decode_jwt(db: Session, token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[JWT_SIGNING_ALGORITHM])
    except jwt.PyJWTError:
        return {}

    username = decoded_token.get("sub")
    if not username:
        return {}

    user = user_service.get_user_by_username(db, username)
    if not user:
        return {}

    expiry = decoded_token.get("exp")

    if expiry < time.time():
        return {}

    return decoded_token


def verify_jwt(db: Session, token: str) -> bool:
    if not decode_jwt(db, token):
        return False

    return True


def get_expiry(expires: int):
    if expires:
        return datetime.utcnow() + timedelta(minutes=expires)

    return datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)


def generate_access_token(data: dict) -> AccessTokenResponse:
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=JWT_SIGNING_ALGORITHM)
    return AccessTokenResponse(access_token=encoded_jwt, token_type="bearer")
