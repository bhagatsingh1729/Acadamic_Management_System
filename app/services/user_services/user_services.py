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
# USER
# =============================================================

def get_user_via_email_service(email: EmailStr, db: Session):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def get_all_user_service(db: Session):
    # Returns empty list if no users — not an error
    return db.query(User).limit(30).all()


def get_user_via_role(role: str, db: Session):
    valid_roles = ["admin", "student", "hod", "faculty", "super_admin"]
    if role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Valid roles: {valid_roles}"
        )
    return db.query(User).filter(User.role == role).limit(30).all()


def change_user_password_service(email: str, new_password: str, db: Session):
    user_db = get_user_via_email_service(email=email, db=db)

    user_db.password = hash_password(new_password)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)

    return {"message": "Password updated successfully", "user_id": user_db.id}