# =============================================================
# api/auth_routes.py
# =============================================================

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.services_schemas.auth_schemas.auth_schema import LoginSchema,TokenResponseSchema
from app.services.auth_services.auth_service import login_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/login",
    response_model=TokenResponseSchema
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),  # ← accepts form data
    db: Session = Depends(get_db)
):
    # form_data.username holds the email (Swagger sends it that way)
    data = LoginSchema(
        email=form_data.username,
        password=form_data.password
    )

    try:
        return login_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
