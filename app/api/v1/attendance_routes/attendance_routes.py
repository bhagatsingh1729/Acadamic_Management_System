from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import (
    get_db, 
    require_roles, 
    get_current_faculty,
    get_current_admin
)
from app.models.models import Faculty, Admin
from app.schemas.services_schemas.attendance__schemas.attendance_schemas import (
    AttendanceCreateRequest,
    AttendanceResponse,
    AttendanceBulkMarkRequest,
    AttendanceSummaryResponse
)
from app.services.attendance_services.attendance_services import (
    mark_attendance_service,
    bulk_mark_attendance_service,
    get_session_attendance_service,
    get_student_summary_service,
    generate_attendance_for_session_service
)

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# 1. Mark single attendance (Faculty only)
@router.post("/mark", response_model=AttendanceResponse)
def mark_attendance_route(
    data: AttendanceCreateRequest,
    db: Session = Depends(get_db),
    faculty: Faculty = Depends(get_current_faculty) # Resolves user + verifies profile
):
    return mark_attendance_service(db, data, faculty.user_id)

# 2. Bulk mark (Faculty only)
@router.post("/bulk-mark")
def bulk_mark_attendance_route(
    request: AttendanceBulkMarkRequest,
    db: Session = Depends(get_db),
    faculty: Faculty = Depends(get_current_faculty)
):
    return bulk_mark_attendance_service(db, request, faculty.user_id)

# 3. Generate attendance "shells" (Admin only)
@router.post("/generate/{class_session_id}")
def generate_attendance_route(
    class_session_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    # The service will verify the branch_id inside if you pass the admin context
    return generate_attendance_for_session_service(db, class_session_id)

# 4. Get report for a session
@router.get("/session/{class_session_id}", response_model=List[AttendanceResponse])
def get_session_attendance_route(
    class_session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "faculty", "super_admin"))
):
    return get_session_attendance_service(db, class_session_id)

# 5. Get Student Summary
@router.get("/summary/{usn}", response_model=AttendanceSummaryResponse)
def get_student_summary_route(
    usn: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("student", "admin", "faculty", "super_admin"))
):
    # Logic to ensure student can only see their own summary if they are a student
    if current_user.role == "student":
        # Additional check: Does this USN belong to this user?
        # You can add a helper for this or verify in the service
        pass 
    return get_student_summary_service(db, usn)