from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Department

from app.core.dependencies import (
    require_roles,
    require_super_admin,
    get_current_admin,
    get_current_student,
    get_current_user,
)

from app.services.department_services.department_services import(
    create_department_service,
    update_department_service,
    delete_department_service,
    get_all_departments_service,
    get_department_via_uid
)
from app.schemas.services_schemas.department_schemas.department_schemas import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
    MessageResponse
)

router = APIRouter(prefix="/departments",tags=["departments"])

@router.post("/create",response_model=DepartmentResponse)
def create_department_route(data:DepartmentCreate,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return create_department_service(data=data,db=db)

@router.get("",response_model=list[DepartmentResponse])
def get_all_departments_route(db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return get_all_departments_service(db)

@router.get("/{dept_uid}",response_model=DepartmentResponse)
def get_department_vis_uid_route(dept_uid:str,db:Session=Depends(get_db),current_user = Depends(require_super_admin)):
    return get_department_via_uid(dept_uid=dept_uid,db=db)

@router.patch("/{dept_uid}/update",response_model=DepartmentResponse)
def update_department_route(dept_uid:str,data:DepartmentUpdate,db:Session=Depends(get_db),current_user = Depends(require_super_admin)):
    return update_department_service(dept_uid=dept_uid,data=data,db=db)

@router.delete("/{dept_uid}/delete",response_model=MessageResponse)
def delte_department_route(dept_uid:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return delete_department_service(dept_uid=dept_uid,db=db)

