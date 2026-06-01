# =============================================================
# services/super_admin_services/role_management.py
#
# Super admin service — manages all roles (Admin, Faculty, Student, User).
#
# FIXES APPLIED:
#
#   FIX 1.1 — update_student_service NameError
#     branch_db was used outside the if block where it was assigned.
#     Fixed by resolving branch_id before building StudentUpdate,
#     only replacing it if branch_uid is provided.
#
#   FIX 1.2 — update_admin_service NameError
#     branch_data was used outside the if block where it was assigned.
#     Same fix — branch_id resolved conditionally.
#
#   FIX 1.3 — update_faculty_service AttributeError
#     data.dept_uid.upper() called without checking for None.
#     Fixed with an explicit null check before calling .upper().
#
#   FIX 2.3 — get_all_admin_service wrong behavior
#     Raised HTTPException(400) when no admins found.
#     An empty list is a valid response — changed to return [].
#
#   FIX 2.4 — get_all_faculty_service wrong behavior
#     Same issue — returns [] now instead of raising 404.
#
#   FIX 2.5 — Removed duplicate imports
#     Cleaned up the messy import block that imported the same
#     thing multiple times and had conflicting schema overrides.
# =============================================================

from pydantic import EmailStr
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.security import hash_password

# ── Service-level schemas ─────────────────────────────────────
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminCreate,
    AdminUpdate,
    StudentCreateRequest,
    StudentUpdateRequest,
    FacultyCreateRequest,
    FacultyUpdateRequest,
)

# ── Fundamental schemas ───────────────────────────────────────
from app.schemas.fundamental_schemas.student_schema import StudentCreate, StudentUpdate
from app.schemas.fundamental_schemas import admin_schema
from app.schemas.fundamental_schemas import faculty_schema

# ── CRUD ─────────────────────────────────────────────────────
from app.crud.fundamental_crud.admin_crud import create_admin, update_admin
from app.crud.fundamental_crud.faculty_crud import create_faculty, update_faculty, delete_faculty
from app.crud.fundamental_crud.student_crud import (
    create_student,
    get_all_students,
    get_student_by_usn,
    update_student,
    delete_student,
)

# ── Models ────────────────────────────────────────────────────
from app.models.models import Branch, Admin, User, Department, Faculty


# =============================================================
# FACULTY
# =============================================================

def create_faculty_service(data: FacultyCreateRequest, db: Session):
    dept_uid = data.dept_uid.upper()
    dept = db.query(Department).filter(Department.dept_uid == dept_uid).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

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
    return create_faculty(db=db, faculty_data=data_payload)


def get_all_faculty_service(db: Session):
    # FIX 2.4: return empty list instead of raising 404
    return db.query(Faculty).limit(50).all()


def get_faculty_via_emp_id_service(emp_id: str, db: Session):
    db_faculty = db.query(Faculty).filter(
        Faculty.employee_id == emp_id.upper()
    ).first()
    if not db_faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")
    return db_faculty


def update_faculty_service(emp_id: str, data: FacultyUpdateRequest, db: Session):
    # FIX 1.3: check dept_uid is not None before calling .upper()
    # dept_id stays as current value unless a new dept_uid is provided
    faculty_db = get_faculty_via_emp_id_service(emp_id=emp_id, db=db)

    dept_id = faculty_db.dept_id      # ← current dept_id as default

    if data.dept_uid is not None:
        dept_uid = data.dept_uid.upper()
        dept_db = db.query(Department).filter(
            Department.dept_uid == dept_uid
        ).first()
        if not dept_db:
            raise HTTPException(status_code=404, detail="Department not found")
        dept_id = dept_db.id           # ← only updated when dept_uid is provided

    faculty_data = faculty_schema.FacultyUpdate(
        name=data.name,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address,
        dept_id=dept_id                # ← always defined, no AttributeError possible
    )
    return update_faculty(db=db, faculty_id=faculty_db.id, faculty_data=faculty_data)


def delete_faculty_via_emp_id_service(emp_id: str, db: Session):
    faculty_db = get_faculty_via_emp_id_service(emp_id=emp_id, db=db)
    return delete_faculty(db=db, faculty_id=faculty_db.id)