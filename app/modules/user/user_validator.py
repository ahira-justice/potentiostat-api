from app.common.data.models import User
from app.common.domain.database import SessionLocal


def is_not_null(value) -> bool:
    if value:
        return True

    return False


def email_is_unique(email) -> bool:
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    db.close()

    if user:
        return False

    return True
