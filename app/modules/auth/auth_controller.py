from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.common.data.dtos import ErrorResponse, ValidationErrorResponse
from app.common.domain.constants import AUTH_URL
from app.common.domain.database import get_db
from app.modules.auth import auth_service
from app.modules.auth.auth_dtos import AccessTokenResponse, ClientLoginRequest, ResetPasswordRequest, \
    ForgotPasswordRequest, LoginRequest
from app.modules.user.user_dtos import UserResponse

controller = APIRouter(
    prefix=AUTH_URL,
    tags=["Auth"]
)


@controller.post(
    path="/login",
    status_code=200,
    responses={
        200: {"model": AccessTokenResponse},
        401: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def get_access_token_for_user(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """Generate access token for valid user credentials"""
    return auth_service.get_access_token_for_user(db, login_data)


@controller.post(
    path="/client-login",
    status_code=200,
    responses={
        200: {"model": AccessTokenResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def get_access_token_for_client(
        request: ClientLoginRequest,
        db: Session = Depends(get_db)
):
    """Generate access token for valid client credentials"""
    return auth_service.get_access_token_for_client(db, request)


@controller.post(
    path="/forgot-password",
    status_code=204,
    responses={
        204: {},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def forgot_password(
        forgot_password_data: ForgotPasswordRequest,
        db: Session = Depends(get_db)
):
    """Generate password reset link"""
    auth_service.forgot_password(db, forgot_password_data)


@controller.post(
    path="/reset-password",
    status_code=200,
    responses={
        200: {"model": UserResponse},
        404: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def reset_password(
        reset_password_data: ResetPasswordRequest,
        db: Session = Depends(get_db)
):
    """Reset user password"""
    return auth_service.reset_password(db, reset_password_data)
