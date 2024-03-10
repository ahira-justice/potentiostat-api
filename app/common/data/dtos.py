from typing import Dict, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: Optional[str]


class ValidationErrorResponse(ErrorResponse):
    errors: Dict[str, str]
