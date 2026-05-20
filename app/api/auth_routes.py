from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.auth_schema import LoginSchema
from app.schemas.auth_schema import TokenResponseSchema

from app.services.auth_service import login_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponseSchema
)
def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):

    try:

        return login_user(
            db,
            data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )