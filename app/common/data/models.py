from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, BigInteger, LargeBinary, String
from sqlalchemy.orm import relationship

from app.common.domain.database import Base


class BaseEntity(Base):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, index=True)
    created_on = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_on = Column(DateTime, default=None, onupdate=datetime.utcnow, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)


class User(BaseEntity):
    __tablename__ = "users"

    first_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    phone_number = Column(String, unique=True, nullable=True, index=True)
    password_hash = Column(LargeBinary, nullable=True)
    password_salt = Column(LargeBinary, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_staff = Column(Boolean, nullable=False, default=False)


class UserToken(BaseEntity):
    __tablename__ = "user_tokens"

    token = Column(String, nullable=False, index=True)
    token_type = Column(String, nullable=False)
    expiry = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    user = relationship("User")
