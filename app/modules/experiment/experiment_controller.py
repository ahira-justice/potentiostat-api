from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm.session import Session

from app.common.auth.bearer import BearerAuth
from app.common.data.dtos import ErrorResponse, ValidationErrorResponse
from app.common.domain.constants import EXPERIMENTS_URL
from app.common.domain.database import get_db
from app.common.pagination import PageResponse
from app.modules.experiment import experiment_service
from app.modules.experiment.experiment_dtos import ExperimentResponse, ExperimentCreateRequest
from app.modules.experiment.experiment_queries import SearchExperimentsQuery
from app.modules.measurement.measurement_dtos import MeasurementResponse

controller = APIRouter(
    prefix=EXPERIMENTS_URL,
    tags=["Experiments"]
)


@controller.post(
    path="",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": ExperimentResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def create_experiment(
        experiment_data: ExperimentCreateRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """Create new experiment"""
    return await experiment_service.create_experiment(db, request, experiment_data)


@controller.get(
    path="",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": PageResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    }
)
async def search_experiments(
        request: Request,
        query: SearchExperimentsQuery = Depends(),
        db: Session = Depends(get_db)
):
    """Search experiments"""
    return experiment_service.search_experiments(db, request, query)


@controller.get(
    path="/{id}",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": ExperimentResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def get_experiment(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """Get experiment by id"""
    return experiment_service.get_experiment(db, id, request)


@controller.get(
    path="/{id}/measurements",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": List[MeasurementResponse]},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def get_experiment_measurements(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """Get experiment measurements by id"""
    return experiment_service.get_experiment_measurements(db, id, request)


@controller.put(
    path="/{id}/start",
    dependencies=[Depends(BearerAuth())],
    status_code=204,
    responses={
        204: {},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def start_experiment(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """Start experiment"""
    experiment_service.start_experiment(db, id, request)


@controller.put(
    path="/{id}/stop",
    dependencies=[Depends(BearerAuth())],
    status_code=204,
    responses={
        204: {},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def stop_experiment(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """Stop experiment"""
    experiment_service.stop_experiment(db, id, request)

