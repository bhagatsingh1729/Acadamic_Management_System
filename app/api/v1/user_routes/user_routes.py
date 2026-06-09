# app/api/user_routes.py
from fastapi import APIRouter, Depends
from app.models.models import User
from app.core.dependencies import get_current_user  # 👈 Import your dependency
from app.schemas.response_schemas.base_response import UserBasicInfo

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/me",response_model=UserBasicInfo)
def read_current_user(current_user: User = Depends(get_current_user)):  # 👈 Use it here
    #return {"id": current_user.id, "email": current_user.email, "name":current_user.name, "role":current_user.role}
    return current_user
    

# =============================================================
# USER routes added by bhagat
# =============================================================

from sqlalchemy.orm import Session
from app.schemas.response_schemas.base_response import UserBasicInfo
from app.database import get_db
from app.core.dependencies import require_super_admin

from app.services.user_services.user_services import (
    get_all_user_service,
    get_user_via_role,
    get_user_via_email_service,
    change_user_password_service
)

from app.schemas.services_schemas.role_management_schemas.user_schemas import PasswordChangeRequest



@router.get("", response_model=list[UserBasicInfo])
def get_all_users_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_user_service(db)


@router.get("/role/{role}", response_model=list[UserBasicInfo])
def get_all_user_via_role(
    role: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_user_via_role(role, db)


@router.get("/{email}", response_model=UserBasicInfo)
def get_user_via_email_route(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_user_via_email_service(email, db)

@router.patch("/password/update/me")
def change_my_password_route(
    data: PasswordChangeRequest,       
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return change_user_password_service(
        email=current_user.email,
        new_password=data.new_password,
        db=db
    )
    


@router.patch("/password/{email}")
def change_user_password_route(
    email: str,
    data: PasswordChangeRequest,       # FIX 1.6: password now in request body, not URL
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return change_user_password_service(
        email=email,
        new_password=data.new_password,
        db=db
    )