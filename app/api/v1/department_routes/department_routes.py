from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Department

from app.core.dependencies import (
    require_super_admin,
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
from app.schemas.response_schemas.API_Response import ApiResponse

router = APIRouter(prefix="/departments",tags=["departments"])

@router.post("/create",response_model=ApiResponse[DepartmentResponse])
def create_department_route(data:DepartmentCreate,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    result = create_department_service(data=data,db=db)
    return ApiResponse(success=True,message='successfully created department',data=result)

@router.get("",response_model=ApiResponse[list[DepartmentResponse]])
def get_all_departments_route(db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    result = get_all_departments_service(db)
    return ApiResponse(success=True,message='all departments',data=result)

@router.get("/{dept_uid}",response_model=ApiResponse[DepartmentResponse])
def get_department_vis_uid_route(dept_uid:str,db:Session=Depends(get_db),current_user = Depends(require_super_admin)):
    result = get_department_via_uid(dept_uid=dept_uid,db=db)
    return ApiResponse(success=True,message='department data',data=result)

@router.patch("/{dept_uid}/update",response_model=ApiResponse[DepartmentResponse])
def update_department_route(dept_uid:str,data:DepartmentUpdate,db:Session=Depends(get_db),current_user = Depends(require_super_admin)):
    result = update_department_service(dept_uid=dept_uid,data=data,db=db)
    return ApiResponse(success=True,message='updated department successfully',data=result)

@router.delete("/{dept_uid}/delete",response_model=ApiResponse[None])
def delte_department_route(dept_uid:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    delete_department_service(dept_uid=dept_uid,db=db)
    return ApiResponse(success=True,message='deleted department successully',data=None)

