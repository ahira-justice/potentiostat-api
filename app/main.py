from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from logging.config import fileConfig as configure_logging
from loguru import logger

from app.common.config.loguru_logging_intercept import setup_loguru_logging_intercept
from app.common.data.migrations_manager import migrate_database
from app.common.domain.config import ENVIRONMENT, SQLALCHEMY_DATABASE_URL
from app.common.domain.constants import ALEMBIC_INI_DIR, LOGGING_CONFIG_DIR, DOCS_URL, MIGRATIONS_DIR, OPEN_API_URL
from app.common.exceptions.app_exceptions import AppDomainException
from app.common.exceptions.handlers import exception_handler, app_exception_handler, validation_exception_handler
from app.common.middleware.handlers import http_logging_middleware
from app.modules.auth.auth_controller import controller as auth_controller
from app.modules.client.client_controller import controller as client_controller
from app.modules.experiment.experiment_controller import controller as experiment_controller
from app.modules.measurement.measurement_controller import controller as measurement_controller
from app.modules.user.user_controller import controller as user_controller
from app.modules.user_token.user_token_controller import controller as user_token_controller


configure_logging(LOGGING_CONFIG_DIR, disable_existing_loggers=False)
setup_loguru_logging_intercept(
    modules=(
        "uvicorn", "uvicorn.access", "uvicorn.error", "alembic", "sqlalchemy.engine"
        )
)


if ENVIRONMENT != "TEST":
    migrate_database(MIGRATIONS_DIR, ALEMBIC_INI_DIR, SQLALCHEMY_DATABASE_URL)


app = FastAPI(
    title="potentiostat API",
    version="1.0",
    openapi_url=OPEN_API_URL,
    docs_url=DOCS_URL
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(request: Request, e: RequestValidationError):
    return await validation_exception_handler(request, e)


@app.exception_handler(AppDomainException)
async def custom_app_exception_handler(request: Request, e: AppDomainException):
    return await app_exception_handler(request, e)


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, e: Exception):
    return await exception_handler(request, e)


@app.middleware("http")
async def custom_http_logging_middleware(request: Request, call_next):
    return await http_logging_middleware(request, call_next)


app.include_router(auth_controller)
app.include_router(client_controller)
app.include_router(experiment_controller)
app.include_router(measurement_controller)
app.include_router(user_controller)
app.include_router(user_token_controller)


@app.get("/", include_in_schema=False)
async def index():
    response = RedirectResponse(url=DOCS_URL)
    logger.info(f"Redirecting to swagger docs; {DOCS_URL}")

    return response
