# =============================================================
# api/v1/super_admin_routes/role_management_routes.py
#
# FIXES APPLIED:
#
#   FIX 1.6 — Password passed as query parameter (security hole)
#     change_user_password_route was receiving new_password as
#     a query param, meaning it appeared in the URL and got logged.
#     Fixed: new_password now comes from a request body via
#     PasswordChangeRequest schema.
#
#   FIX 1.7 — Route conflict: /{usn} matching non-student paths
#     Routes GET "" and GET /{usn} at the bottom were dangerous —
#     "/{usn}" could match "/admins", "/faculty" etc.
#     Removed the duplicate GET "" (list_students) since
#     GET /students already does the same thing.
#     Kept GET /students/{usn} with explicit prefix to avoid ambiguity.
#
#   ALSO FIXED — Removed unused imports
# =============================================================

from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.database import get_db
from app.core.dependencies import require_super_admin

from app.services.super_admin_services.role_management import (
    # Admin
    create_admin_service,
    get_all_admin_service,
    get_user_via_email_service,
    get_all_user_service,
    get_user_via_role,
    update_admin_service,
    # Faculty
    create_faculty_service,
    update_faculty_service,
    delete_faculty_via_emp_id_service,
    get_all_faculty_service,
    get_faculty_via_emp_id_service,
    # Student
    create_student_service,
    get_all_students_service,
    update_student_service,
    delete_student_service,
    get_student_by_usn_service,
    # User
    change_user_password_service,
)
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminCreate,
    AdminUpdate,
    AdminResponse,
    StudentCreateRequest,
    StudentUpdateRequest,
    StudentResponse,
    FacultyCreateRequest,
    FacultyUpdateRequest,
    FacultyResponse,
    PasswordChangeRequest,             # FIX 1.6: new schema for body-based password change
)
from app.schemas.response_schemas.base_response import UserBasicInfo


router = APIRouter(prefix="/roles", tags=["Role Management"])


# =============================================================
# ADMIN
# =============================================================

@router.post("/admins/create", response_model=AdminResponse)
def create_admin_route(
    data: AdminCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return create_admin_service(data=data, db=db)


@router.get("/admins", response_model=list[AdminResponse])
def get_all_admin_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_admin_service(db)


@router.patch("/admins/update/{email}", response_model=AdminResponse)
def update_admin_route(
    email: str,
    data: AdminUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return update_admin_service(email=email, data=data, db=db)


# =============================================================
# USER
# =============================================================

@router.get("/users", response_model=list[UserBasicInfo])
def get_all_users_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_user_service(db)


@router.get("/users/role/{role}", response_model=list[UserBasicInfo])
def get_all_user_via_role(
    role: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_user_via_role(role, db)


@router.get("/users/{email}", response_model=UserBasicInfo)
def get_user_via_email_route(
    email: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_user_via_email_service(email, db)


@router.patch("/users/password/{email}")
def change_user_password_route(
    email: str,
    data: PasswordChangeRequest,       # FIX 1.6: password now in request body, not URL
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return change_user_password_service(
        email=email,
        new_password=data.new_password,
        db=db
    )


# =============================================================
# FACULTY
# =============================================================

@router.post("/faculty/create", response_model=FacultyResponse)
def create_faculty_route(
    data: FacultyCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return create_faculty_service(db=db, data=data)


@router.get("/faculty", response_model=list[FacultyResponse])
def get_all_faculty_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_faculty_service(db)


@router.get("/faculty/{emp_id}", response_model=FacultyResponse)
def get_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_faculty_via_emp_id_service(emp_id=emp_id, db=db)


@router.patch("/faculty/update/{emp_id}", response_model=FacultyResponse)
def update_faculty_via_emp_id_route(
    emp_id: str,
    data: FacultyUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return update_faculty_service(emp_id, data, db)


@router.delete("/faculty/delete/{emp_id}")
def delete_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return delete_faculty_via_emp_id_service(emp_id=emp_id, db=db)


# =============================================================
# STUDENT
# FIX 1.7: Removed GET "" and GET /{usn} that caused route conflicts.
# All student routes now have explicit /students/ prefix.
# =============================================================

@router.post("/students/create", response_model=StudentResponse)
def create_student_route(
    data: StudentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return create_student_service(data=data, db=db)


@router.get("/students", response_model=list[StudentResponse])
def get_all_students_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_students_service(db=db)


@router.get("/students/{usn}", response_model=StudentResponse)
def get_student_by_usn_route(
    usn: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_student_by_usn_service(db, usn)


@router.put("/students/update/{usn}", response_model=StudentResponse)
def update_student_route(
    usn: str,
    data: StudentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return update_student_service(db, usn, data)


@router.delete("/students/delete/{usn}")
def delete_student_route(
    usn: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return delete_student_service(db, usn)
