from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm.session import Session

from app.common.auth.bearer import BearerAuth
from app.common.data.dtos import ErrorResponse, ValidationErrorResponse
from app.common.domain.constants import USERS_URL
from app.common.domain.database import get_db
from app.common.pagination import PageResponse
from app.modules.user import user_service
from app.modules.user.user_dtos import UserResponse, UserCreateRequest, UserUpdateRequest, UserAdminStatusRequest
from app.modules.user.user_queries import SearchUsersQuery

controller = APIRouter(
    prefix=USERS_URL,
    tags=["Users"]
)


@controller.post(
    path="",
    status_code=200,
    responses={
        200: {"model": UserResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def create_user(
        user_data: UserCreateRequest,
        db: Session = Depends(get_db)
):
    """Create new user"""
    return user_service.create_user(db, user_data)


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
async def search_users(
        request: Request,
        query: SearchUsersQuery = Depends(),
        db: Session = Depends(get_db)
):
    """Search users"""
    return user_service.search_users(db, request, query)


@controller.get(
    path="/me",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": UserResponse},
        401: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def get_current_user_details(
        request: Request,
        db: Session = Depends(get_db)
):
    """Get current user details"""
    return user_service.get_current_user_details(db, request)


@controller.get(
    path="/{id}",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": UserResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def get_user(
        id: int,
        request: Request,
        db: Session = Depends(get_db)
):
    """Get user by id"""
    return user_service.get_user(db, id, request)


@controller.put(
    path="/{id}",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": UserResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def update_user(
        id: int,
        user_data: UserUpdateRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """Update user"""
    return user_service.update_user(db, id, request, user_data)


@controller.put(
    path="/{id}/admin-status",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": UserResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def change_admin_status(
        id: int,
        user_admin_status: UserAdminStatusRequest,
        request: Request,
        db: Session = Depends(get_db)
):
    """Update user admin status"""
    return user_service.change_admin_status(db, id, user_admin_status, request)
