from pydantic import BaseModel


class VerifyUserTokenRequest(BaseModel):
    username: str
    token: str
    token_type: str
