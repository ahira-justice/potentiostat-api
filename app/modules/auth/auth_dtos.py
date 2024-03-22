from typing import Optional

from pydantic import BaseModel

from app.common.domain.config import ACCESS_TOKEN_EXPIRE_IN_SECONDS


class LoginRequest(BaseModel):
    username: str
    password: str
    expires: Optional[int] = ACCESS_TOKEN_EXPIRE_IN_SECONDS


class ClientLoginRequest(BaseModel):
    client_id: str
    client_secret: str
    expires: Optional[int] = ACCESS_TOKEN_EXPIRE_IN_SECONDS


class ForgotPasswordRequest(BaseModel):
    username: str


class ResetPasswordRequest(BaseModel):
    username: str
    password: str
    token: str


class PasswordDto(BaseModel):
    password_hash: bytes
    password_salt: bytes


class ClientSecretDto(BaseModel):
    secret_hash: bytes
    secret_salt: bytes


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
