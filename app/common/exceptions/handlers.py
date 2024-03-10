from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse

from app.common.data.dtos import ErrorResponse
from app.common.exceptions.app_exceptions import AppDomainException, SystemErrorException


async def validation_exception_handler(request: Request, ex: RequestValidationError) -> JSONResponse:
    errors = {}

    for error in jsonable_encoder(ex.errors()):
        errors[error["loc"][1]] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "UnprocessableEntity",
            "message": "Validation error",
            "errors": errors
        },
    )


async def app_exception_handler(request: Request, ex: AppDomainException) -> JSONResponse:
    response_body = {"code": ex.code}

    if ex.message:
        response_body["message"] = ex.message

    return JSONResponse(
        status_code=ex.status_code,
        content=response_body
    )


async def exception_handler(request: Request, ex: Exception) -> JSONResponse:
    logger.error(ex)

    ex = SystemErrorException()

    return JSONResponse(
        status_code=ex.status_code,
        content={
            "code": ex.code,
            "message": ex.message,
        },
    )
