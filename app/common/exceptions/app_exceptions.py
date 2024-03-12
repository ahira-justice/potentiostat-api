from pydantic import BaseModel


class AppDomainException(Exception):
    def __init__(self, status_code: int, code: str, message: str = None):
        self.status_code = status_code
        self.code = code
        self.message = message

    def __str__(self):
        return f"Error: \n\nCode: {self.code}\n\nMessage: {self.message}"


class BadRequestException(AppDomainException):
    def __init__(self, message: str):
        status_code = 400
        code = "BadRequest"
        super().__init__(status_code, code, message)


class ForbiddenException(AppDomainException):
    def __init__(self, username: str = None):
        status_code = 403
        code = "Forbidden"

        if username:
            message = f"Unauthorized: {username} is not allowed to access or change this resource"
            super().__init__(status_code, code, message)
            return

        super().__init__(status_code, code)


class NotFoundException(AppDomainException):
    def __init__(self, message: str = None, name: str = None, key: BaseModel = None):
        status_code = 404
        code = "NotFound"

        if not message and (name and key):
            message = f"Resource \"{name}\" ({key}) was not found"
        elif not message:
            raise ValueError("Pass \"message\" argument or a combination of \"name\" and \"key\"")

        super().__init__(status_code, code, message)


class SystemErrorException(AppDomainException):
    def __init__(self, message: str = None):
        status_code = 500
        code = "SystemError"

        if not message:
            message = "An unexpected error occurred. Please try again or confirm current operation status"

        super().__init__(status_code, code, message)


class UpstreamServerException(AppDomainException):
    def __init__(self, message: str):
        status_code = 502
        code = "BadGateway"
        super().__init__(status_code, code, message)


class UnauthorizedRequestException(AppDomainException):
    def __init__(self, message: str):
        status_code = 401
        code = "Unauthorized"
        super().__init__(status_code, code, message)
