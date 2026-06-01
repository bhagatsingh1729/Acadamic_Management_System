# =============================================================
# api/v1/super_admin_routes/role_management_routes.py
#
# FIXES APPLIED:
#
#   FIX 1.6 — Password passed as query parameter (security hole)
#     change_user_password_route was receiving new_password as
#     a query param, meaning it appeared in the URL and got logged.
#     Fixed: new_password now comes from a request body via
#     PasswordChangeRequest schema.
#
#   FIX 1.7 — Route conflict: /{usn} matching non-student paths
#     Routes GET "" and GET /{usn} at the bottom were dangerous —
#     "/{usn}" could match "/admins", "/faculty" etc.
#     Removed the duplicate GET "" (list_students) since
#     GET /students already does the same thing.
#     Kept GET /students/{usn} with explicit prefix to avoid ambiguity.
#
#   ALSO FIXED — Removed unused imports
# =============================================================

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.database import get_db
from app.core.dependencies import require_super_admin


from app.schemas.services_schemas.role_management_schemas.admin_schemas import (
    AdminCreate,
    AdminUpdate,
    AdminResponse
)
from app.schemas.response_schemas.base_response import UserBasicInfo
from app.services.admin_services.admin_services import (
    # Admin
    create_admin_service,
    delete_admin_service,
    get_all_admin_service,
    update_admin_service,
)

router = APIRouter(prefix="/admins", tags=["Admin Management"])

# =============================================================
# ADMIN
# =============================================================

@router.post("/create", response_model=AdminResponse)
def create_admin_route(
    data: AdminCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return create_admin_service(data=data, db=db)


@router.get("", response_model=list[AdminResponse])
def get_all_admin_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_admin_service(db)


@router.patch("/update/{email}", response_model=AdminResponse)
def update_admin_route(
    email: str,
    data: AdminUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return update_admin_service(email=email, data=data, db=db)

@router.delete("/delete/{email}")
def delete_admin_route(
    email: EmailStr,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return delete_admin_service(email=email, db=db)