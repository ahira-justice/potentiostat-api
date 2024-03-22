import hashlib
import string
import time
from datetime import datetime, timedelta

import jwt
from sqlalchemy.orm.session import Session

from app.common import utils
from app.common.data.enums import UserTokenType
from app.common.data.models import User, Client
from app.common.domain.config import USER_TOKEN_RESET_PASSWORD_EXPIRE_MINUTES, USER_TOKEN_RESET_PASSWORD_LENGTH, \
    ACCESS_TOKEN_EXPIRE_IN_SECONDS, JWT_SIGNING_ALGORITHM, SECRET_KEY
from app.common.domain.constants import FORGOT_PASSWORD_TEMPLATE
from app.common.exceptions.app_exceptions import UnauthorizedRequestException, NotFoundException
from app.modules.auth.auth_dtos import ForgotPasswordRequest, PasswordDto, ResetPasswordRequest, LoginRequest, \
    AccessTokenResponse, ClientLoginRequest, ClientSecretDto
from app.modules.client import client_service
from app.modules.email import email_service
from app.modules.user import user_service
from app.modules.user.user_dtos import UserResponse
from app.modules.user.user_mappings import user_to_user_response
from app.modules.user_token import user_token_service


def get_user_password(user: User) -> PasswordDto:
    return PasswordDto(
        password_hash=user.password_hash,
        password_salt=user.password_salt
    )


def get_client_secret(db: Session, client_id: str) -> ClientSecretDto:
    client = client_service.get_client_by_identifier(db, client_id)

    response = ClientSecretDto(
        secret_hash=client.secret_hash,
        secret_salt=client.secret_salt
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
    try:
        user = user_service.get_user_by_username(db, username)
    except NotFoundException:
        return False

    user_password = get_user_password(user)

    if not user_password:
        return False

    if not verify_password(password, user_password.password_hash, user_password.password_salt):
        return False

    return True


def authenticate_client(db: Session, client_id: str, secret: str) -> bool:
    try:
        client_secret = get_client_secret(db, client_id)
    except NotFoundException:
        return False

    if not client_secret:
        return False

    if not verify_password(secret, client_secret.secret_hash, client_secret.secret_salt):
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


def get_access_token_for_user(db: Session, login_data: LoginRequest) -> AccessTokenResponse:
    if not authenticate_user(db, login_data.username, login_data.password):
        raise UnauthorizedRequestException("Incorrect username or password")

    expiry = get_expiry(login_data.expires)

    data = {"sub": login_data.username, "exp": expiry}
    return generate_access_token(data)


def get_access_token_for_client(db: Session, request: ClientLoginRequest) -> AccessTokenResponse:
    if not authenticate_client(db, request.client_id, request.client_secret):
        raise UnauthorizedRequestException("Incorrect client identifier or secret")

    expire = get_expiry(request.expires)

    data = {"client_id": request.client_id, "exp": expire}
    return generate_access_token(data)


def decode_jwt(db: Session, token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[JWT_SIGNING_ALGORITHM])
    except jwt.PyJWTError:
        return {}

    username = decoded_token.get("sub")
    client_id = decoded_token.get("client_id")

    if not username and not client_id:
        return {}

    user = db.query(User).filter(User.username == username).first()
    client = db.query(Client).filter(Client.identifier == client_id).first()

    if not user and not client:
        return {}

    expiry = decoded_token.get("exp")

    if expiry < time.time():
        return {}

    return decoded_token


def verify_jwt(db: Session, token: str) -> bool:
    if not decode_jwt(db, token):
        return False

    return True


def get_expiry(expires: int) -> datetime:
    if expires:
        return datetime.utcnow() + timedelta(seconds=expires)

    return datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_IN_SECONDS)


def generate_access_token(data: dict) -> AccessTokenResponse:
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=JWT_SIGNING_ALGORITHM)
    expires_in = data.get('exp') - datetime.utcnow()
    return AccessTokenResponse(access_token=encoded_jwt, token_type="bearer", expires_in=expires_in.total_seconds())
