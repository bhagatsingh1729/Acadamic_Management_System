from fastapi import Depends
from fastapi import HTTPException

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.models import User

from app.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="invalid token"
        )

    user_id = payload.get("user_id")

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="invalid token payload"
        )

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="user not found"
        )

    return user


def require_admin(
    current_user = Depends(get_current_user)
):

    if current_user.role != "admin":

        raise HTTPException(
            status_code=403,
            detail="admin access required"
        )

    return current_user


def require_faculty(
    current_user = Depends(get_current_user)
):

    if current_user.role != "faculty":

        raise HTTPException(
            status_code=403,
            detail="faculty access required"
        )

    return current_user


def require_student(
    current_user = Depends(get_current_user)
):

    if current_user.role != "student":

        raise HTTPException(
            status_code=403,
            detail="student access required"
        )

    return current_user


def require_hod(
    current_user = Depends(get_current_user)
):

    if current_user.role != "hod":

        raise HTTPException(
            status_code=403,
            detail="hod access required"
        )

    return current_user