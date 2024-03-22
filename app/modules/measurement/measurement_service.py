from typing import List

from fastapi import Request
from sqlalchemy.orm.session import Session

from app.common.data.enums import ExperimentStatus
from app.common.data.models import Measurement, Experiment, Client
from app.common.exceptions.app_exceptions import ForbiddenException, BadRequestException
from app.modules.client import client_service
from app.modules.experiment import experiment_service
from app.modules.measurement.measurement_dtos import MeasurementCreateRequest, MeasurementResponse
from app.modules.measurement.measurement_mappings import measurement_to_measurement_response


def create_measurement(db: Session, request: Request, measurement_data: MeasurementCreateRequest) -> MeasurementResponse:
    logged_in_client = client_service.get_logged_in_client(db, request)
    experiment = experiment_service.get_experiment_by_id(db, measurement_data.experiment_id)

    validate_experiment_belongs_to_logged_in_client(logged_in_client, experiment)
    validate_experiment_is_running(experiment)

    measurement = persist_measurement(db, experiment, measurement_data)

    return measurement_to_measurement_response(measurement)


def validate_experiment_belongs_to_logged_in_client(logged_in_client: Client, experiment: Experiment) -> None:
    if logged_in_client.id != experiment.client_id:
        raise ForbiddenException(logged_in_client.identifier)


def validate_experiment_is_running(experiment: Experiment) -> None:
    if experiment.experiment_status != ExperimentStatus.RUNNING.name:
        raise BadRequestException(f"Cannot post measurements for {experiment.experiment_status} experiment")


def persist_measurement(db: Session, experiment: Experiment, measurement_data: MeasurementCreateRequest):
    measurement = build_measurement(experiment, measurement_data)
    return save_measurement(db, measurement)


def build_measurement(experiment: Experiment, measurement_data: MeasurementCreateRequest) -> Measurement:
    return Measurement(
        timestamp=measurement_data.timestamp,
        voltage=measurement_data.voltage,
        current=measurement_data.current,
        experiment_id=experiment.id
    )


def save_measurement(db, measurement):
    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    return measurement


def get_measurements(db: Session, experiment_id: int) -> List[MeasurementResponse]:
    measurements = db.query(Measurement).filter(Measurement.experiment_id == experiment_id).all()
    return list(map(measurement_to_measurement_response, measurements))
