import os

from dotenv import load_dotenv

from app.common.domain.constants import TEST_DATABASE_URL

load_dotenv()

ENVIRONMENT = os.environ.get("ENVIRONMENT")
ABLY_API_KEY = os.environ.get("ABLY_API_KEY")
SQLALCHEMY_DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
JWT_SIGNING_ALGORITHM = os.environ.get("JWT_SIGNING_ALGORITHM")
ACCESS_TOKEN_EXPIRE_IN_SECONDS = int(os.environ.get("ACCESS_TOKEN_EXPIRE_IN_SECONDS"))
LOG_LEVEL_CONFIG = os.environ.get("LOG_LEVEL_CONFIG", "DEBUG")
JSON_LOGS_CONFIG = os.environ.get("JSON_LOGS_CONFIG", "0")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_FIRST_NAME = os.environ.get("ADMIN_FIRST_NAME")
ADMIN_LAST_NAME = os.environ.get("ADMIN_LAST_NAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
USER_TOKEN_RESET_PASSWORD_EXPIRE_MINUTES = int(os.environ.get("USER_TOKEN_RESET_PASSWORD_EXPIRE_MINUTES"))
USER_TOKEN_RESET_PASSWORD_LENGTH = int(os.environ.get("USER_TOKEN_RESET_PASSWORD_LENGTH"))

if ENVIRONMENT == "TEST":
    SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL
