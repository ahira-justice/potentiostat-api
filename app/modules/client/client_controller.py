from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm.session import Session

from app.common.auth.bearer import BearerAuth
from app.common.data.dtos import ErrorResponse, ValidationErrorResponse
from app.common.domain.constants import CLIENTS_URL
from app.common.domain.database import get_db
from app.common.pagination import PageResponse
from app.modules.client import client_service
from app.modules.client.client_dtos import ClientResponse, ClientCreateRequest
from app.modules.client.client_queries import SearchClientsQuery

controller = APIRouter(
    prefix=CLIENTS_URL,
    tags=["Clients"]
)


@controller.post(
    path="",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": ClientResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def create_client(
        client_data: ClientCreateRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """Create new client"""
    return client_service.create_client(db, request, client_data)


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
async def search_clients(
        request: Request,
        query: SearchClientsQuery = Depends(),
        db: Session = Depends(get_db)
):
    """Search clients"""
    return client_service.search_clients(db, request, query)


@controller.get(
    path="/{id}",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": ClientResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def get_client(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """Get client by id"""
    return client_service.get_client(db, id, request)
