from fastapi import Request
from fastapi.security.http import HTTPBearer

from app.common.domain.database import SessionLocal
from app.common.exceptions.app_exceptions import UnauthorizedRequestException
from app.modules.auth import auth_service


class BearerAuth(HTTPBearer):

    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)
        self.db = SessionLocal()

    async def __call__(self, request: Request):
        authorization = request.headers.get("Authorization", None)

        if not authorization:
            raise UnauthorizedRequestException("Missing or malformed authorization header")

        scheme, token = authorization.split(" ")

        if not scheme or not token:
            raise UnauthorizedRequestException("Missing or malformed authorization header")

        if scheme.lower() != "bearer":
            raise UnauthorizedRequestException("Invalid authentication scheme")

        if not auth_service.verify_jwt(self.db, token):
            raise UnauthorizedRequestException("Invalid or expired token")

        return True
