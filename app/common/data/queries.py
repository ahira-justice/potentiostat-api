from pydantic import BaseModel, conint


class BaseQuery(BaseModel):
    page: conint(ge=0) = 0
    size: conint(ge=1) = 10
