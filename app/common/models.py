from typing import Any

from pydantic import BaseModel


class Notification(BaseModel):
    event: str
    payload: Any
