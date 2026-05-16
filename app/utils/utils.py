from app.database import SessionLocal, get_db
from sqlalchemy.orm import Session
from app.models.models import User


def get_user(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()


def verify_password(plain_password, hashed_password):
    raise NotImplementedError("Use app_v2.core.security.verify_password for current password hashing")