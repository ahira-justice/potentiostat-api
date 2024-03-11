from pydantic import BaseModel


class ExperimentResponse(BaseModel):
    id: int
    experiment_status: str
    username: str
    client_id: str


class ExperimentCreateRequest(BaseModel):
    client_id: str
