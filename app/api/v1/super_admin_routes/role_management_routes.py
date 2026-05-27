from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Admin
from app.core.dependencies import (
    require_roles,
    require_super_admin,
    get_current_admin,
    get_current_student,
    get_current_user,
)
from app.services.super_admin_services.role_mangement import (
    create_admin_service,
    get_all_admin_service
)
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminCreate,
    AdminResponse
)
router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/admin/create",response_model=AdminResponse)
def create_admin_route(data:AdminCreate,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return create_admin_service(data=data,db=db)

@router.get("/admins",response_model=list[AdminResponse])
def get_all_admin_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_admin_service(db)
