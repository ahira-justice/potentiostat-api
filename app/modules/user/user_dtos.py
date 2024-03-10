from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from app.common import validators
from app.modules.user import user_validators


class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr]
    phone_number: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_admin: bool = False
    is_staff: bool = False


class UserAdminStatusRequest(BaseModel):
    is_admin: bool = False


class UserCreateRequest(BaseModel):
    username: str
    email: Optional[EmailStr]
    first_name: Optional[str]
    last_name: Optional[str]
    password: str

    @validator("username")
    def username_is_not_null(cls, username):

        if not validators.is_not_null(username):
            raise ValueError("User username cannot be null")

        return username

    @validator("username")
    def username_is_unique(cls, username):

        if not user_validators.email_is_unique(username):
            raise ValueError(f"User with username: '{username}' already registered")

        return username

    @validator("password")
    def password_is_not_null(cls, password):

        if not validators.is_not_null(password):
            raise ValueError("User password cannot be null")

        return password


class UserUpdateRequest(BaseModel):
    email: EmailStr
    phone_number: str
    first_name: str
    middle_name: str
    last_name: str
    password: str

    @validator("email")
    def email_is_not_null(cls, email):

        if not user_validator.is_not_null(email):
            raise ValueError("User email cannot be null")

        return email

    @validator("phone_number")
    def phone_number_is_not_null(cls, phone_number):

        if not user_validator.is_not_null(phone_number):
            raise ValueError("User phone number cannot be null")

        return phone_number

    @validator("last_name")
    def last_name_is_not_null(cls, last_name):

        if not user_validator.is_not_null(last_name):
            raise ValueError("User last name cannot be null")

        return last_name

    @validator("first_name")
    def first_name_is_not_null(cls, first_name):

        if not user_validator.is_not_null(first_name):
            raise ValueError("User first name cannot be null")

        return first_name
