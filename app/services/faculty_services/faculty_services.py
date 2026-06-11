from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.services_schemas.role_management_schemas.faculty_schemas import (
    FacultyCreateRequest,
    FacultyUpdateRequest,
    BulkFacultyCreateRequest,
    BulkFacultyCreateResponse,
    FacultyCreateResultItem,
)
from app.schemas.fundamental_schemas import faculty_schema
from app.models.models import Department, Faculty
import app.crud.fundamental_crud.faculty_crud as faculty_crud

# =============================================================
# SINGLE CREATE
# =============================================================
def create_faculty_service(data: FacultyCreateRequest, db: Session):
    dept_uid = data.dept_uid.upper()
    dept = db.query(Department).filter(Department.dept_uid == dept_uid).first()
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Department '{data.dept_uid}' not found"
        )

    data_payload = faculty_schema.FacultyCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        employee_id=data.employee_id,
        dept_id=dept.id,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )
    
    try:
        faculty = faculty_crud.create_faculty(db=db, faculty_data=data_payload)
        db.commit()
        db.refresh(faculty)
        return faculty
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database constraint error occurred."
        )


# =============================================================
# BULK CREATE
# =============================================================
def bulk_create_faculty_service(data: BulkFacultyCreateRequest, db: Session) -> BulkFacultyCreateResponse:
    results = []
    successful_count = 0
    failed_count = 0

    for faculty_req in data.faculties:
        normalized_emp_id = faculty_req.employee_id.upper()
        email = faculty_req.email
        
        try:
            with db.begin_nested():  # Valid row checkpoints now work because CRUD doesn't commit early
                dept_uid = faculty_req.dept_uid.upper()
                dept = db.query(Department).filter(Department.dept_uid == dept_uid).first()
                if not dept:
                    raise ValueError(f"Department '{faculty_req.dept_uid}' not found")

                data_payload = faculty_schema.FacultyCreate(
                    name=faculty_req.name,
                    email=faculty_req.email,
                    password=faculty_req.password,
                    employee_id=faculty_req.employee_id,
                    dept_id=dept.id,
                    phone_no=faculty_req.phone_no,
                    dob=faculty_req.dob,
                    address=faculty_req.address
                )
                faculty_crud.create_faculty(db=db, faculty_data=data_payload)
                
            successful_count += 1
            results.append(FacultyCreateResultItem(
                employee_id=normalized_emp_id,
                email=email,
                status="Success",
                detail="Faculty profile staged successfully"
            ))
            
        except ValueError as ve:
            failed_count += 1
            results.append(FacultyCreateResultItem(
                employee_id=normalized_emp_id,
                email=email,
                status="Failed",
                detail=str(ve)
            ))
        except Exception:
            failed_count += 1
            results.append(FacultyCreateResultItem(
                employee_id=normalized_emp_id,
                email=email,
                status="Failed",
                detail="Database core validation failure"
            ))

    if successful_count > 0:
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Critical error committing batch data operations."
            )

    return BulkFacultyCreateResponse(
        total_processed=len(data.faculties),
        successful=successful_count,
        failed=failed_count,
        results=results
    )


# =============================================================
# READ SERVICES
# =============================================================
def get_all_faculty_service(db: Session):
    return faculty_crud.get_all_faculty(db)


def get_faculty_via_emp_id_service(emp_id: str, db: Session):
    db_faculty = faculty_crud.get_faculty_by_emp_id(db, emp_id)
    if not db_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty record not found")
    return db_faculty


# =============================================================
# UPDATE SERVICE
# =============================================================
def update_faculty_service(emp_id: str, data: FacultyUpdateRequest, db: Session):
    faculty_db = get_faculty_via_emp_id_service(emp_id=emp_id, db=db)
    dept_id = faculty_db.dept_id 

    if data.dept_uid is not None:
        dept_uid = data.dept_uid.upper()
        dept_db = db.query(Department).filter(Department.dept_uid == dept_uid).first()
        if not dept_db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
        dept_id = dept_db.id 

    faculty_data = faculty_schema.FacultyUpdate(
        name=data.name,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address,
        dept_id=dept_id 
    )
    
    try:
        updated_faculty = faculty_crud.update_faculty(db=db, faculty_id=faculty_db.id, faculty_data=faculty_data)
        db.commit()
        db.refresh(updated_faculty)
        return updated_faculty
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


# =============================================================
# DELETE SERVICE
# =============================================================
def delete_faculty_via_emp_id_service(emp_id: str, db: Session):
    faculty_db = get_faculty_via_emp_id_service(emp_id=emp_id, db=db)
    try:
        faculty_crud.delete_faculty(db=db, faculty_id=faculty_db.id)
        db.commit()
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))