from fastapi import Request
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from app.common.data.models import Client
from app.common.exceptions.app_exceptions import ForbiddenException, NotFoundException
from app.common.pagination import paginate, page_to_page_response, PageResponse
from app.modules.client.client_dtos import ClientCreateRequest, ClientResponse
from app.modules.client.client_mappings import client_create_to_client, client_to_client_response
from app.modules.client.client_queries import SearchClientsQuery
from app.modules.user import user_service


def create_client(db: Session, request: Request, client_data: ClientCreateRequest) -> ClientResponse:
    logged_in_user = user_service.get_logged_in_user(db, request)

    if not logged_in_user.is_admin:
        raise ForbiddenException(logged_in_user.username)

    client = client_create_to_client(client_data)

    db.add(client)
    db.commit()
    db.refresh(client)

    return client_to_client_response(client)


def search_clients(db: Session, request: Request, query: SearchClientsQuery) -> PageResponse:
    logged_in_user = user_service.get_logged_in_user(db, request)

    if not logged_in_user.is_admin:
        raise ForbiddenException(logged_in_user.username)

    db_query = filter_clients(db, query)

    page = paginate(db_query, query.page, query.size)
    page.content = list(map(client_to_client_response, page.content))

    return page_to_page_response(page)


def filter_clients(db: Session, query: SearchClientsQuery) -> Query:
    db_query = db.query(Client)

    if query.name is not None:
        db_query = db_query.filter(Client.name.contains(query.name))

    return db_query


def get_client_by_identifier(db: Session, client_id: str) -> Client:
    client = db.query(Client).filter(Client.identifier == client_id).first()

    if not client:
        raise NotFoundException(message=f"Client with client identifier: {client_id} does not exist")

    return client


def get_client(db: Session, id: int, request: Request) -> ClientResponse:
    logged_in_user = user_service.get_logged_in_user(db, request)

    if not logged_in_user.is_admin:
        raise ForbiddenException(logged_in_user.username)

    client = get_client_by_id(db, id)

    return client_to_client_response(client)


def get_client_by_id(db: Session, id: int) -> Client:
    client = db.query(Client).filter(Client.id == id).first()

    if not client:
        raise NotFoundException(message=f"Client with id: {id} does not exist")

    return client
