from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.core.dependencies import require_super_admin, require_roles
from app.schemas.response_schemas.API_Response import ApiResponse

from app.schemas.services_schemas.role_management_schemas.faculty_schemas import (
    FacultyCreateRequest,
    FacultyUpdateRequest,
    FacultyResponse,
    BulkFacultyCreateRequest,
    BulkFacultyCreateResponse,
)
import app.services.faculty_services.faculty_services as faculty_services

router = APIRouter(prefix="/faculty", tags=["Faculty Management"])

# =============================================================
# POST: CREATE SINGLE FACULTY
# =============================================================
@router.post("", response_model=ApiResponse[FacultyResponse])
def create_faculty_route(
    data: FacultyCreateRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('super_admin'))
):
    result = faculty_services.create_faculty_service(data=data, db=db)
    return ApiResponse(
        success=True,
        message="Faculty profile generated successfully.",
        data=result
    )


# =============================================================
# POST: BULK CREATE FACULTIES
# =============================================================
@router.post("/bulk", response_model=ApiResponse[BulkFacultyCreateResponse])
def bulk_create_faculties_route(
    data: BulkFacultyCreateRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('super_admin'))
):
    result = faculty_services.bulk_create_faculty_service(data=data, db=db)
    return ApiResponse(
        success=True,
        message=f"Batch execution completed. Success: {result.successful}, Failed: {result.failed}",
        data=result
    )


# =============================================================
# GET: LIST ALL FACULTIES
# =============================================================
@router.get("", response_model=ApiResponse[List[FacultyResponse]])
def get_all_faculty_route(
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    result = faculty_services.get_all_faculty_service(db)
    return ApiResponse(success=True, message='faculties list retrieved', data=result)


# =============================================================
# GET: RETRIEVE SINGLE PROFILE VIA EMP_ID
# =============================================================
@router.get("/{emp_id}", response_model=ApiResponse[FacultyResponse])
def get_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    result = faculty_services.get_faculty_via_emp_id_service(emp_id=emp_id, db=db)
    return ApiResponse(success=True, message='faculty matched', data=result)


# =============================================================
# PATCH: UPDATE PROFILE VIA EMP_ID
# =============================================================
@router.patch("/update/{emp_id}", response_model=ApiResponse[FacultyResponse])
def update_faculty_via_emp_id_route(
    emp_id: str,
    data: FacultyUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    result = faculty_services.update_faculty_service(emp_id, data, db)
    return ApiResponse(success=True, message='faculty profile updated', data=result)


# =============================================================
# DELETE: REMOVE PROFILE VIA EMP_ID
# =============================================================
@router.delete("/delete/{emp_id}", response_model=ApiResponse[None])
def delete_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    faculty_services.delete_faculty_via_emp_id_service(emp_id=emp_id, db=db)
    return ApiResponse(success=True, message='faculty deleted successfully', data=None)