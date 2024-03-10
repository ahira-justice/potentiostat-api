from pydantic import BaseModel, validator

from app.common import validators
from app.modules.client import client_validators


class ClientResponse(BaseModel):
    id: int
    identifier: str


class ClientCreateRequest(BaseModel):
    identifier: str
    secret: str

    @validator("identifier")
    def identifier_is_not_null(cls, identifier):

        if not validators.is_not_null(identifier):
            raise ValueError("Client identifier cannot be null")

        return identifier

    @validator("identifier")
    def identifier_is_unique(cls, identifier):

        if not client_validators.identifier_is_unique(identifier):
            raise ValueError(f"Client with identifier: '{identifier}' already registered")

        return identifier

    @validator("secret")
    def secret_is_not_null(cls, secret):

        if not validators.is_not_null(secret):
            raise ValueError("Client secret cannot be null")

        return secret
