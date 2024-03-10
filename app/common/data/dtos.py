from typing import Dict

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str


class ValidationErrorResponse(ErrorResponse):
    errors: Dict[str, str]
