from decimal import Decimal

from pydantic import BaseModel, Field


class ExperimentResponse(BaseModel):
    id: int
    experiment_status: str
    start_voltage: Decimal
    end_voltage: Decimal
    scan_rate: Decimal
    username: str
    client_id: str


class ExperimentCreateRequest(BaseModel):
    client_id: str
    start_voltage: Decimal = Field(decimal_places=4)
    end_voltage: Decimal = Field(decimal_places=4)
    scan_rate: Decimal = Field(decimal_places=4)
