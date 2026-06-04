from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import (
    get_db, 
    require_roles, 
    get_current_faculty,
    get_current_admin
)
from app.models.models import Faculty, Admin, FacultySubject, Student, Subject,BranchSubject
from app.schemas.services_schemas.attendance__schemas.attendance_schemas import (
    AttendanceCreateRequest,
    AttendanceResponse,
    AttendanceBulkMarkRequest,
    AttendanceSummaryResponse
)
from app.services.attendance_services.attendance_services import (
    get_student_subject_attendance,
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
        # Simply fetch the student record attached to the current user
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        # Verify the USN in the URL matches the USN of the logged-in student
        if not student or student.usn.upper() != usn.upper():
            raise HTTPException(status_code=403, detail="You can only view your own attendance")

    return get_student_summary_service(db, usn)

@router.get("/student/{usn}/subject/{subject_code}", response_model=List[AttendanceSummaryResponse])
def get_student_subject_attendance_route(
    usn: str,
    subject_code: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("student", "admin", "faculty", "super_admin"))
):
    usn = usn.upper()
    subject_code = subject_code.upper()


    # Logic to ensure student can only see their own summary if they are a student
    # ROBUST ISOLATION:
    if current_user.role == "student":
        # Simply fetch the student record attached to the current user
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        # Verify the USN in the URL matches the USN of the logged-in student
        if not student or student.usn != usn:
            raise HTTPException(status_code=403, detail="You can only view your own attendance")
    if current_user.role == "faculty":
        # Additional check: Does this faculty teach this subject?
        faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        subject = db.query(Subject).filter(Subject.code == subject_code).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        faculty_subject = db.query(FacultySubject).filter(
            FacultySubject.faculty_id == faculty.id,
            FacultySubject.subject_id == subject.id
        ).first()
        if not faculty_subject:
            raise HTTPException(status_code=403, detail="You are not authorized to view this attendance data")
    
    if current_user.role == "admin":
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin:
            raise HTTPException(status_code=404,detail='admin not assigned as admin properly yet')
        student_db = db.query(Student).filter(Student.usn == usn).first()
        if not student_db:
            raise HTTPException(status_code=404,detail='student not found')
        if student_db.branch_id != admin.branch_id:
            raise HTTPException(status_code=403,detail="you're not authorized to access this student attendance")
        
        subject = db.query(Subject).filter(Subject.code == subject_code).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")
        
        subject_branch_check = db.query(BranchSubject).filter(BranchSubject.subject_id == subject.id,BranchSubject.branch_id == admin.branch_id).first()

        if not subject_branch_check:
            raise HTTPException(status_code=403,detail='you are not authorized to see attendance for this subject')
    
    try:
        return get_student_subject_attendance(db, usn, subject_code)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))