from decimal import Decimal

from pydantic import BaseModel, Field


class MeasurementResponse(BaseModel):
    id: int
    timestamp: int
    voltage: Decimal
    current: Decimal
    experiment_id: int


class MeasurementCreateRequest(BaseModel):
    experiment_id: int
    timestamp: int
    voltage: Decimal = Field(decimal_places=4)
    current: Decimal = Field(decimal_places=4)
