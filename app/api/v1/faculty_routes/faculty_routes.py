from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.database import get_db
from app.core.dependencies import require_super_admin

from app.schemas.services_schemas.role_management_schemas.faculty_schemas import FacultyResponse
from app.services.faculty_services.faculty_services import (
    create_faculty_service,
    update_faculty_service,
    delete_faculty_via_emp_id_service,
    get_all_faculty_service,
    get_faculty_via_emp_id_service,
)
from app.schemas.services_schemas.role_management_schemas.faculty_schemas import (
    FacultyCreateRequest,
    FacultyUpdateRequest,
    FacultyResponse,
)
from app.schemas.response_schemas.base_response import UserBasicInfo

router = APIRouter(prefix="/faculty", tags=["Faculty Management"])

# =============================================================
# FACULTY
# =============================================================

@router.post("/create", response_model=FacultyResponse)
def create_faculty_route(
    data: FacultyCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return create_faculty_service(db=db, data=data)


@router.get("", response_model=list[FacultyResponse])
def get_all_faculty_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_faculty_service(db)


@router.get("/{emp_id}", response_model=FacultyResponse)
def get_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_faculty_via_emp_id_service(emp_id=emp_id, db=db)


@router.patch("/update/{emp_id}", response_model=FacultyResponse)
def update_faculty_via_emp_id_route(
    emp_id: str,
    data: FacultyUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return update_faculty_service(emp_id, data, db)


@router.delete("/delete/{emp_id}")
def delete_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return delete_faculty_via_emp_id_service(emp_id=emp_id, db=db)
