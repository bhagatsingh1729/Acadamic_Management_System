# =============================================================
# api/v1/student_routes.py
#
# All student endpoints with full RBAC enforcement.
# =============================================================
#
# RBAC RULES FOR STUDENTS:
#
#   POST   /students              admin (own branch only) | super_admin
#   GET    /students              admin (own branch) | super_admin | faculty | hod
#   GET    /students/me           student (own record only)
#   GET    /students/{usn}        admin (own branch) | super_admin | faculty | hod
#   GET    /students/cohort       admin (own branch) | super_admin
#   PUT    /students/{id}         admin (own branch) | super_admin
#   DELETE /students/{id}         admin (own branch) | super_admin
#
# HOW OWNERSHIP IS ENFORCED HERE:
#
#   For admin role:
#     1. get_current_admin dependency returns the Admin DB record
#     2. admin.branch_id is passed to service as enforced_branch_id
#     3. Service rejects any request for a different branch
#
#   For super_admin role:
#     1. require_super_admin dependency verifies role
#     2. enforced_branch_id=None is passed to service
#     3. Service skips the branch check (super_admin can do everything)
#
#   For faculty/hod role (read-only):
#     1. They can READ all students
#     2. No create/update/delete access
#
#   For student role:
#     1. /me endpoint uses get_current_student
#     2. Returns ONLY that student's own record
#     3. No access to other students' data
#
# =============================================================

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Admin, Student ,HOD
from app.core.dependencies import (
    require_roles,
    require_super_admin,
    get_current_admin,
    get_current_student,
    get_current_user,
)
from app.schemas.services_schemas.role_management_schemas.student_schemas import (
    StudentCreateRequest,
    StudentUpdateRequest,
)
from app.schemas.services_schemas.role_management_schemas.student_schemas import StudentResponse
from app.services.student_services.student_service import (
    create_student_service,
    get_all_students_service,
    get_student_by_usn_service,
    get_students_by_cohort_service,
    update_student_service,
    delete_student_service,
)


router = APIRouter(prefix="/students", tags=["Students"])


# =============================================================
# POST /students — Create student
# =============================================================
@router.post(
    "",
    response_model=StudentResponse,
    summary="Create a student [admin | super_admin]"
)
def create_student(
    data: StudentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
    # ↑ Only admin and super_admin can create students.
    #   require_roles returns the User object.
):
    # ─── Branch-scoping logic ─────────────────────────────────
    # Admin → can only create for their own branch
    # Super admin → can create for any branch
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()

        return create_student_service(
            db,
            data,
            enforced_branch_id=admin.branch_id   # ← scoped to admin's branch
        )

    # Super admin has no branch restriction
    return create_student_service(db, data, enforced_branch_id=None)


# =============================================================
# GET /students/me — Student views their own profile
# IMPORTANT: /me must come BEFORE /{usn}
# Because if /{usn} comes first, FastAPI matches /me as a usn.
# =============================================================
@router.get(
    "/me",
    response_model=StudentResponse,
    summary="Get own profile [student only]"
)
def get_my_profile(
    student: Student = Depends(get_current_student)
    # ↑ get_current_student:
    #   1. Verifies JWT token
    #   2. Checks role == "student"
    #   3. Returns the Student DB record for that user
    #   The student can ONLY get their own record this way.
    #   There's no way for them to access another student's profile.
):
    return student


# =============================================================
# GET /students — List students
# =============================================================
@router.get(
    "",
    response_model=list[StudentResponse],
    summary="List students [admin (own branch) | super_admin | faculty | hod]"
)
def list_students(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty", "hod"))
):
    # Admin → only their branch students
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        return get_all_students_service(db, enforced_branch_id=admin.branch_id)

    


    # super_admin, faculty, hod → all students
    return get_all_students_service(db, enforced_branch_id=None)


# =============================================================
# GET /students/cohort — Filter by semester/batch/section
# =============================================================
@router.get(
    "/cohort",
    response_model=list[StudentResponse],
    summary="Get students by cohort [admin | super_admin]"
)
def get_cohort(
    semester: int = Query(..., ge=1, le=8),
    batch: str = Query(...),
    section: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        branch_id = admin.branch_id
    else:
        # super_admin must pass branch_id as query param
        # (handled differently — for now raise error)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Super admin must use /students endpoint with branch filtering"
        )

    return get_students_by_cohort_service(
        db,
        semester=semester,
        batch=batch,
        section=section,
        enforced_branch_id=branch_id
    )

# =============================================================
# GET /students/{usn}
# ⚠️ All static paths (/me, /cohort) must be above this.
# =============================================================
@router.get("/{usn}", response_model=StudentResponse, summary="Get student by USN [admin | super_admin | faculty | hod]")
def get_student(
    usn: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty", "hod"))
):
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        return get_student_by_usn_service(db, usn, enforced_branch_id=admin.branch_id)

    return get_student_by_usn_service(db, usn, enforced_branch_id=None)


# =============================================================
# PATCH /students/{usn}
# ⚠️ Removed /update/ prefix — it would collide with GET /{usn}
#    treating "update" as a USN string.
# =============================================================
@router.patch("/{usn}", response_model=StudentResponse, summary="Update student [admin | super_admin]")
def update_student(
    usn: str,
    data: StudentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        return update_student_service(db, usn, data, enforced_branch_id=admin.branch_id)

    return update_student_service(db, usn, data, enforced_branch_id=None)


# =============================================================
# DELETE /students/{usn}
# ⚠️ Same — removed /delete/ prefix for the same reason.
# =============================================================
@router.delete("/{usn}", summary="Delete student [admin | super_admin]")
def delete_student(
    usn: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        return delete_student_service(db, usn, enforced_branch_id=admin.branch_id)

    return delete_student_service(db, usn, enforced_branch_id=None)