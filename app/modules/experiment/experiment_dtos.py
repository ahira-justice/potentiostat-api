from decimal import Decimal

from pydantic import BaseModel, Field


class ExperimentResponse(BaseModel):
    id: int
    experiment_status: str
    start_voltage: Decimal
    end_voltage: Decimal
    voltage_step: Decimal
    username: str
    client_id: str


class ExperimentCreateRequest(BaseModel):
    client_id: str
    start_voltage: Decimal = Field(decimal_places=7)
    end_voltage: Decimal = Field(decimal_places=7)
    voltage_step: Decimal = Field(decimal_places=7)
