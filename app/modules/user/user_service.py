from fastapi import Request
from pydantic import EmailStr
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session

from app.common import utils
from app.common.data.models import User
from app.common.exceptions.app_exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.common.pagination import paginate, page_to_page_response, PageResponse
from app.modules.auth import auth_service
from app.modules.user.user_dtos import UserCreateRequest, UserResponse, UserAdminStatusRequest, UserUpdateRequest
from app.modules.user.user_mappings import user_create_to_user, user_to_user_response
from app.modules.user.user_queries import SearchUsersQuery


def create_user(db: Session, user_data: UserCreateRequest) -> UserResponse:
    user = user_create_to_user(user_data)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user_to_user_response(user)


def seed_user(db: Session, username: str, first_name: str, last_name: str, password: str) -> UserResponse:
    payload = UserCreateRequest(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password
    )

    admin_user = create_user(db, payload)
    return admin_user


def set_super_admin(db: Session, id: int):
    user = db.query(User).filter(User.id == id).first()
    user.is_admin = True
    user.is_staff = True

    db.commit()
    db.refresh(user)

    return user_to_user_response(user)


def change_admin_status(db: Session, id: int, user_admin_status: UserAdminStatusRequest,
                        request: Request) -> UserResponse:
    logged_in_user = get_logged_in_user(db, request)

    if not logged_in_user.is_staff:
        raise ForbiddenException(logged_in_user.username)

    user = get_user_by_id(db, id)

    if user.is_staff:
        raise BadRequestException("Cannot modify admin status of super admin user")

    user.is_admin = user_admin_status.is_admin

    db.commit()
    db.refresh(user)

    response = user_to_user_response(user)

    return response


def update_user(db: Session, id: int, request: Request, user_data: UserUpdateRequest) -> UserResponse:
    logged_in_user = get_logged_in_user(db, request)

    password_hash, password_salt = utils.generate_hash_and_salt(user_data.password)

    user = get_user_by_id(db, id)

    if user.is_staff:
        raise BadRequestException("Cannot modify super admin user")

    if user.username != logged_in_user.username:
        raise ForbiddenException(logged_in_user.username)

    user_data_username = user_data.email if user_data.email else user_data.phone_number

    if get_user_by_username(db, user_data_username) and user.username != user_data_username:
        raise BadRequestException(f"Cannot update username. User with username: '{user_data_username}' already exists")

    user.username = user_data_username
    user.email = user_data.email
    user.first_name = user_data.first_name
    user.middle_name = user_data.middle_name
    user.last_name = user_data.last_name
    user.password_hash = password_hash
    user.password_salt = password_salt

    db.commit()
    db.refresh(user)

    return user_to_user_response(user)


def search_users(db: Session, request: Request, query: SearchUsersQuery) -> PageResponse:
    logged_in_user = get_logged_in_user(db, request)

    if not logged_in_user.is_admin:
        raise ForbiddenException(logged_in_user.username)

    db_query = filter_users(db, query)

    page = paginate(db_query, query.page, query.size)
    page.content = list(map(user_to_user_response, page.content))

    return page_to_page_response(page)


def filter_users(db: Session, query: SearchUsersQuery) -> Query:
    db_query = db.query(User)

    if query.username is not None:
        db_query = db_query.filter(User.username.contains(query.username))
    if query.email is not None:
        db_query = db_query.filter(User.email.contains(query.email))
    if query.first_name is not None:
        db_query = db_query.filter(User.first_name.contains(query.first_name))
    if query.middle_name is not None:
        db_query = db_query.filter(User.middle_name.contains(query.middle_name))
    if query.last_name is not None:
        db_query = db_query.filter(User.last_name.contains(query.last_name))

    return db_query


def get_user(db: Session, id: int, request: Request) -> UserResponse:
    logged_in_user = get_logged_in_user(db, request)
    user = get_user_by_id(db, id)

    if not logged_in_user.is_admin and logged_in_user.username != user.username:
        raise ForbiddenException(logged_in_user.username)

    return user_to_user_response(user)


def get_current_user_details(db: Session, request: Request) -> UserResponse:
    user = get_current_user(db, request)
    return user_to_user_response(user)


def get_logged_in_user(db: Session, request: Request) -> User:
    try:
        return get_current_user(db, request)
    except NotFoundException:
        raise ForbiddenException()


def get_current_user(db: Session, request: Request) -> User:
    username = get_username_from_token(db, request)
    return get_user_by_username(db, username)


def get_username_from_token(db: Session, request: Request) -> EmailStr:
    token = request.headers.get("Authorization").split(" ")[1]
    payload = auth_service.decode_jwt(db, token)
    return payload.get("sub")


def get_user_by_username(db: Session, username: str) -> User:
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise NotFoundException(message=f"User with username: {username} does not exist")

    return user


def get_user_by_id(db: Session, id: int) -> User:
    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise NotFoundException(message=f"User with id: {id} does not exist")

    return user
