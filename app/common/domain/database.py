from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.common.domain.config import SQLALCHEMY_DATABASE_URL, database_type

engine = create_engine(SQLALCHEMY_DATABASE_URL)

if database_type() == "sqlite":
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Provide db session to path operation functions"""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
