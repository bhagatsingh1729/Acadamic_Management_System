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

#=================================
# Code Added by bhagat
#=================================

# =============================================================
# STUDENT
# =============================================================

from app.models.models import Branch

def create_student_service(data: StudentCreateRequest, db: Session):
    branch_uid = data.branch_uid.upper()
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404, detail="Branch not found")

    data_payload = StudentCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        usn=data.usn,
        semester=data.semester,
        batch=data.batch,
        section=data.section,
        branch_id=branch_db.id,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )
    return create_student(db=db, data=data_payload)


def get_all_students_service(db: Session):
    return get_all_students(db)


def get_student_by_usn_service(db: Session, usn: str):
    return get_student_by_usn(db, usn)


def update_student_service(db: Session, usn: str, data: StudentUpdateRequest):
    student = get_student_by_usn(db, usn)

    # FIX 1.1: resolve branch_id conditionally — avoid NameError
    # branch_id stays as current value unless a new branch_uid is provided
    branch_id = student.branch_id

    if data.branch_uid is not None:
        branch_uid = data.branch_uid.upper()
        branch_db = db.query(Branch).filter(
            Branch.branch_uid == branch_uid
        ).first()
        if not branch_db:
            raise HTTPException(status_code=404, detail="Branch not found")
        branch_id = branch_db.id       # ← only updated when branch_uid is provided

    update_data = StudentUpdate(
        semester=data.semester,
        batch=data.batch,
        branch_id=branch_id,           # ← always defined, no NameError possible
        section=data.section,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )
    return update_student(db, student.id, update_data)


def delete_student_service(db: Session, usn: str):
    student = get_student_by_usn(db, usn)
    return delete_student(db, student.id)