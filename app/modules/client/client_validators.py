from app.common.data.models import Client
from app.common.domain.database import SessionLocal


def identifier_is_unique(identifier) -> bool:
    db = SessionLocal()
    user = db.query(Client).filter(Client.identifier == identifier).first()
    db.close()

    if user:
        return False

    return True
