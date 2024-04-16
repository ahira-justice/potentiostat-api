from typing import List, Union, Optional

from fastapi import Request
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from app.common import notifications
from app.common.data.enums import ExperimentStatus
from app.common.data.models import Experiment, User, Client
from app.common.exceptions.app_exceptions import ForbiddenException, NotFoundException, BadRequestException, \
    UpstreamServerException
from app.common.models import Notification
from app.common.pagination import paginate, page_to_page_response, PageResponse
from app.modules.client import client_service
from app.modules.experiment.experiment_dtos import ExperimentCreateRequest, ExperimentResponse
from app.modules.experiment.experiment_mappings import experiment_to_experiment_response
from app.modules.experiment.experiment_queries import SearchExperimentsQuery
from app.modules.measurement import measurement_service
from app.modules.measurement.measurement_dtos import MeasurementResponse
from app.modules.user import user_service


async def create_experiment(db: Session, request: Request, experiment_data: ExperimentCreateRequest) -> ExperimentResponse:
    logged_in_user = user_service.get_logged_in_user(db, request)
    client = client_service.get_client_by_identifier(db, experiment_data.client_id)

    validate_experiment_creation_request(db, client)

    experiment = persist_experiment(db, logged_in_user, client, experiment_data)
    response = experiment_to_experiment_response(experiment)

    try:
        await notify_client(client, response)
    except UpstreamServerException as ex:
        db.delete(experiment)
        db.commit()
        raise ex

    return response


def validate_experiment_creation_request(db: Session, client: Client):
    unfinished_experiment = get_unfinished_experiment_for_client(db, client)

    if unfinished_experiment is not None:
        raise BadRequestException(
            f"An experiment in the {unfinished_experiment.experiment_status} state already exists for this client"
        )


def get_unfinished_experiment_for_client(db: Session, client: Client) -> Experiment:
    return db.query(Experiment).filter(Experiment.experiment_status != ExperimentStatus.COMPLETED.name,
                                       Experiment.client_id == client.id).first()


def persist_experiment(db: Session, logged_in_user: User, client: Client, request: ExperimentCreateRequest) -> Experiment:
    experiment = build_experiment(logged_in_user, client, request)
    return save_experiment(db, experiment)


def build_experiment(logged_in_user: User, client: Client, request: ExperimentCreateRequest) -> Experiment:
    return Experiment(
        experiment_status=ExperimentStatus.INITIATED.name,
        start_voltage=request.start_voltage,
        end_voltage=request.end_voltage,
        voltage_step=request.voltage_step,
        user_id=logged_in_user.id,
        client_id=client.id
    )


def save_experiment(db: Session, experiment: Experiment) -> Experiment:
    db.add(experiment)
    db.commit()
    db.refresh(experiment)

    return experiment


async def notify_client(client: Client, experiment: ExperimentResponse) -> None:
    notification = build_notification(experiment)
    await notifications.notify(client.identifier, notification)


def build_notification(experiment: ExperimentResponse) -> Notification:
    return Notification(event="experiment.created", payload=experiment)


def search_experiments(db: Session, request: Request, query: SearchExperimentsQuery) -> PageResponse:
    logged_in_user = user_service.get_logged_in_user(db, request)

    db_query = filter_experiments(db, query, logged_in_user)

    page = paginate(db_query, query.page, query.size)
    page.content = list(map(experiment_to_experiment_response, page.content))

    return page_to_page_response(page)


def filter_experiments(db: Session, query: SearchExperimentsQuery, logged_in_user: User) -> Query:
    db_query = db.query(Experiment)

    if query.experiment_status is not None:
        db_query = db_query.filter(Experiment.experiment_status == query.experiment_status)
    if query.username is not None:
        db_query = db_query.join(User).filter(User.username.contains(query.username))
    if query.client_id is not None:
        db_query = db_query.join(Client).filter(Client.identifier.contains(query.client_id))

    if not logged_in_user.is_admin:
        db_query = db_query.filter(Experiment.user_id == logged_in_user.id)

    return db_query


def get_experiment(db: Session, id: int, request: Request) -> ExperimentResponse:
    logged_in_user = user_service.get_logged_in_user(db, request)
    experiment = get_experiment_by_id(db, id)

    if not logged_in_user.is_admin and logged_in_user.id != experiment.user_id:
        raise ForbiddenException(logged_in_user.username)

    return experiment_to_experiment_response(experiment)


def get_experiment_measurements(db: Session, id: int, request: Request) -> List[MeasurementResponse]:
    logged_in_user = user_service.get_logged_in_user(db, request)
    experiment = get_experiment_by_id(db, id)

    if not logged_in_user.is_admin and logged_in_user.id != experiment.user_id:
        raise ForbiddenException(logged_in_user.username)

    return measurement_service.get_measurements(db, experiment.id)


def get_experiment_by_id(db: Session, id: int) -> Experiment:
    experiment = db.query(Experiment).filter(Experiment.id == id).first()

    if not experiment:
        raise NotFoundException(message=f"Experiment with id: {id} does not exist")

    return experiment


def start_experiment(db, id, request) -> None:
    logged_in_client = client_service.get_logged_in_client(db, request)
    experiment = get_experiment_by_id(db, id)

    validate_experiment_belongs_to_logged_in_client(logged_in_client, experiment)
    validate_experiment_is_initiated(experiment)

    experiment.experiment_status = ExperimentStatus.RUNNING.name
    save_experiment(db, experiment)


def validate_experiment_belongs_to_logged_in_client(logged_in_client: Client, experiment: Experiment) -> None:
    if logged_in_client.id != experiment.client_id:
        raise ForbiddenException(logged_in_client.identifier)


def validate_experiment_is_initiated(experiment: Experiment) -> None:
    if experiment.experiment_status != ExperimentStatus.INITIATED.name:
        raise BadRequestException(f"Cannot start {experiment.experiment_status} experiment")


def stop_experiment(db, id, request) -> None:
    logged_in_user = get_logged_in_user(db, request)
    logged_in_client = get_logged_in_client(db, request)

    if not logged_in_user and not logged_in_client:
        raise ForbiddenException()

    experiment = get_experiment_by_id(db, id)

    validate_experiment_belongs_to_logged_in_user_or_client(logged_in_user, logged_in_client, experiment)
    validate_experiment_is_not_completed(experiment)

    experiment.experiment_status = ExperimentStatus.COMPLETED.name
    save_experiment(db, experiment)


def get_logged_in_user(db: Session, request: Request) -> Optional[User]:
    try:
        return user_service.get_logged_in_user(db, request)
    except ForbiddenException:
        return None


def get_logged_in_client(db: Session, request: Request) -> Optional[Client]:
    try:
        return client_service.get_logged_in_client(db, request)
    except ForbiddenException:
        return None


def validate_experiment_belongs_to_logged_in_user_or_client(logged_in_user: User, logged_in_client: Client, experiment: Experiment) -> None:
    if logged_in_user and logged_in_user.id != experiment.user_id:
        raise ForbiddenException(logged_in_user.username)

    if logged_in_client and logged_in_client.id != experiment.client_id:
        raise ForbiddenException(logged_in_client.identifier)


def validate_experiment_is_not_completed(experiment: Experiment) -> None:
    if experiment.experiment_status == ExperimentStatus.COMPLETED.name:
        raise BadRequestException("Experiment is already completed")
