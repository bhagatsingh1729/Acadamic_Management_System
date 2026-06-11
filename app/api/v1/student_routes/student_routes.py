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

from typing import List
from fastapi import APIRouter, Depends, Query,HTTPException,status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Admin, Student
from app.core.dependencies import (
    require_roles,
    get_current_student,
)
from app.schemas.services_schemas.role_management_schemas.student_schemas import (
    StudentCreateRequest,
    StudentUpdateRequest,
    BulkStudentCreateRequest,
    BulkStudentCreateResponse,
)
from app.schemas.services_schemas.role_management_schemas.student_schemas import StudentResponse
from app.services.student_services.student_service import (
    create_student_service,
    bulk_create_student_service,
    get_all_students_service,
    get_student_by_usn_service,
    get_students_by_cohort_service,
    update_student_service,
    delete_student_service,
)
from app.schemas.response_schemas.API_Response import ApiResponse

router = APIRouter(prefix="/students", tags=["Students"])


# =============================================================
# ROUTE: CREATE SINGLE STUDENT
# =============================================================
@router.post("", response_model=ApiResponse[StudentResponse])
def create_student_route(
    data: StudentCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('admin', 'super_admin'))
):
    """
    Endpoint used by admin and super_admin to create a single student.
    - super_admin: Can create a student in any branch.
    - admin: Can ONLY create a student matching their own branch_id.
    """
    enforced_branch_id = None
    
    # Enforce branch restriction for lower-tier admin accounts
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Admin profile configuration missing."
            )
        enforced_branch_id = admin.branch_id

    # Call the core creation pipeline (handles individual transaction rollback/commit)
    result = create_student_service(
        db=db, 
        data=data, 
        enforced_branch_id=enforced_branch_id
    )
    
    return ApiResponse(
        success=True,
        message='Student profile generated successfully.',
        data=result
    )


# =============================================================
# ROUTE: BULK CREATE STUDENTS
# =============================================================
@router.post("/bulk", response_model=ApiResponse[BulkStudentCreateResponse])
def bulk_create_students_route(
    data: BulkStudentCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('admin', 'super_admin'))
):
    """
    Endpoint used by admin and super_admin to batch-create multiple students.
    Uses nested savepoints under the hood to ensure bad rows don't abort good ones.
    - super_admin: Can bulk import students across different branches.
    - admin: Any row pointing to a branch outside their scope will fail gracefully.
    """
    enforced_branch_id = None
    
    # Enforce branch restriction for lower-tier admin accounts
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Admin profile configuration missing."
            )
        enforced_branch_id = admin.branch_id

    # Call the bulk service pipeline (manages savepoint checkpoints for row-isolation)
    result = bulk_create_student_service(
        db=db, 
        data=data, 
        enforced_branch_id=enforced_branch_id
    )
    
    return ApiResponse(
        success=True,
        message=f"Bulk creation completed. Processing metrics -> Success: {result.successful}, Failed: {result.failed}",
        data=result
    )


# =============================================================
# GET /students/me — Student views their own profile
# IMPORTANT: /me must come BEFORE /{usn}
# Because if /{usn} comes first, FastAPI matches /me as a usn.
# =============================================================
@router.get(
    "/me",
    response_model=ApiResponse[StudentResponse],
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
    result = student
    return ApiResponse(success=True,message='your student profile',data=result)


# =============================================================
# GET /students — List students
# =============================================================
@router.get(
    "",
    response_model=ApiResponse[list[StudentResponse]],
    summary="List students [admin (own branch) | super_admin | faculty | hod]"
)
def list_students(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty", "hod"))
):
    enforced_branch_id = None
    # Admin → only their branch students
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_id = admin.branch_id

    


    # super_admin, faculty, hod → all students
    result = get_all_students_service(db, enforced_branch_id=enforced_branch_id)
    return ApiResponse(success=True,message='list of students',data=result)


# =============================================================
# GET /students/cohort — Filter by semester/batch/section
# =============================================================
@router.get(
    "/cohort",
    response_model=ApiResponse[List[StudentResponse]],
    summary="Get students by cohort [admin | super_admin]"
)
def get_cohort(
    semester: int = Query(..., ge=1, le=8),
    batch: str = Query(...),
    section: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    branch_id = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        branch_id = admin.branch_id

    result = get_students_by_cohort_service(
        db,
        semester=semester,
        batch=batch,
        section=section,
        enforced_branch_id=branch_id
    )

    return ApiResponse(success=True, message="Cohort fetched successfully.", data=result)

# =============================================================
# GET /students/{usn}
# ⚠️ All static paths (/me, /cohort) must be above this.
# =============================================================
@router.get("/{usn}", response_model=ApiResponse[StudentResponse], summary="Get student by USN [admin | super_admin | faculty | hod]")
def get_student(
    usn: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty", "hod"))
):
    enforced_branch_id = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_id = admin.branch_id

    result = get_student_by_usn_service(db, usn, enforced_branch_id=enforced_branch_id)

    return ApiResponse(success=True,message='student data filtered by usn',data=result)


# =============================================================
# PATCH /students/{usn}
# ⚠️ Removed /update/ prefix — it would collide with GET /{usn}
#    treating "update" as a USN string.
# =============================================================
@router.patch("/{usn}", response_model=ApiResponse[StudentResponse], summary="Update student [admin | super_admin]")
def update_student(
    usn: str,
    data: StudentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    enforced_branch_id = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_id = admin.branch_id

    result = update_student_service(db, usn, data, enforced_branch_id=enforced_branch_id)
    return ApiResponse(success=True,message='student updated',data=result)


# =============================================================
# DELETE /students/{usn}
# ⚠️ Same — removed /delete/ prefix for the same reason.
# =============================================================
@router.delete("/{usn}",response_model=ApiResponse[None], summary="Delete student [admin | super_admin]")
def delete_student(
    usn: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    enforced_branch_id = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_id = admin.branch_id

    delete_student_service(db, usn, enforced_branch_id=enforced_branch_id)

    return ApiResponse(success=True,message='student deleted successfully',data=None)