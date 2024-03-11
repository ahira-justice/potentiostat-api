from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm.session import Session

from app.common.auth.bearer import BearerAuth
from app.common.data.dtos import ValidationErrorResponse
from app.common.domain.constants import MEASUREMENTS_URL
from app.common.domain.database import get_db
from app.modules.measurement import measurement_service
from app.modules.measurement.measurement_dtos import MeasurementResponse, MeasurementCreateRequest

controller = APIRouter(
    prefix=MEASUREMENTS_URL,
    tags=["Measurements"]
)


@controller.post(
    path="",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": MeasurementResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def create_measurement(
        measurement_data: MeasurementCreateRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """Create new measurement"""
    return measurement_service.create_measurement(db, request, measurement_data)
