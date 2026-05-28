from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import EmailStr
#====================
# Models
#====================
from app.models.models import Admin
#====================
from app.core.dependencies import require_super_admin

#=========================
# Service level Schema
#=========================
from app.services.super_admin_services.role_management import (
    create_admin_service,
    get_all_admin_service,
    get_user_via_email_service,
    get_all_user_service,
    get_user_via_role,
    #student
    create_student_service,
    get_all_students_service
)
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminCreate,
    AdminResponse,
    StudentCreateRequest,
    StudentUpdateRequest,
    StudentResponse
)
from app.schemas.response_schemas.base_response import UserBasicInfo
#===========================================


router = APIRouter(prefix="/roles", tags=["roles"])

@router.post("/admin/create",response_model=AdminResponse)
def create_admin_route(data:AdminCreate,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return create_admin_service(data=data,db=db)

@router.get("/admins",response_model=list[AdminResponse])
def get_all_admin_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_admin_service(db)

@router.get("/users/{email}",response_model=UserBasicInfo)
def get_user_via_email_route(email:EmailStr,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_user_via_email_service(email,db)

@router.get("/users",response_model=list[UserBasicInfo])
def get_all_users_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_user_service(db)

@router.get("/users/role/{role}",response_model=list[UserBasicInfo])
def get_all_user_via_role(role:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_user_via_role(role,db)

#-----------------------------------------
# Student role management
#-----------------------------------------

@router.post("/students/create",response_model=StudentResponse)
def create_student_route(data:StudentCreateRequest,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return create_student_service(data=data,db=db)

@router.get("/students",response_model=list[StudentResponse])
def get_all_students_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_students_service(db=db)