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
# ADMIN
# =============================================================

def create_admin_service(data: AdminCreate, db: Session):
    branch_uid = data.branch_uid.upper()
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404, detail="Branch not found")

    data_payload = admin_schema.AdminCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        branch_id=branch_db.id,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )
    return create_admin(db=db, admin_data=data_payload)


def get_all_admin_service(db: Session):
    # FIX 2.3: return empty list instead of raising 400
    return db.query(Admin).all()


def update_admin_service(data: AdminUpdate, email: EmailStr, db: Session):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="User is not an admin")

    db_admin = db.query(Admin).filter(Admin.user_id == db_user.id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin profile not found")

    # FIX 1.2: resolve branch_id conditionally — avoid NameError
    # branch_id stays as the current value unless a new branch_uid is given
    branch_id = db_admin.branch_id

    if data.branch_uid:
        branch_data = db.query(Branch).filter(
            Branch.branch_uid == data.branch_uid.upper()
        ).first()
        if not branch_data:
            raise HTTPException(status_code=404, detail="Branch not found")
        branch_id = branch_data.id     # ← only updated when branch_uid is provided

    admin_data = admin_schema.AdminUpdate(
        name=data.name,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address,
        branch_id=branch_id            # ← always defined, no NameError possible
    )
    return update_admin(db, db_admin.id, admin_data=admin_data)

# adding the deletion option 
def delete_admin_service(email: EmailStr, db: Session):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.role != "admin":
        raise HTTPException(status_code=400, detail="User is not an admin")

    db_admin = db.query(Admin).filter(Admin.user_id == db_user.id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin profile not found")

    # Delete the admin profile first
    db.delete(db_admin)
    db.delete(db_user)  # Also delete the associated user account
    db.commit()

    return {
        "message": "admin deleted successfully"
    }