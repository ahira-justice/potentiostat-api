from fastapi import APIRouter, Depends
from sqlalchemy.orm.session import Session

from app.common.auth.bearer import BearerAuth
from app.common.data.dtos import ErrorResponse, ValidationErrorResponse
from app.common.domain.constants import USER_TOKENS_URL
from app.common.domain.database import get_db
from app.modules.user_token import user_token_service
from app.modules.user_token.user_token_dtos import VerifyUserTokenRequest

controller = APIRouter(
    prefix=USER_TOKENS_URL,
    tags=["User Tokens"]
)


@controller.post(
    path="/verify",
    dependencies=[Depends(BearerAuth())],
    status_code=200,
    responses={
        200: {"model": bool},
        401: {"model": ErrorResponse},
        422: {"model": ValidationErrorResponse}
    }
)
async def verify_user_token(
        request: VerifyUserTokenRequest,
        db: Session = Depends(get_db)
):
    """Verify user token"""
    return user_token_service.verify_user_token(db, request)
