from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import case, func
from typing import List

from app.core.dependencies import (
    get_db, 
    require_roles, 
    get_current_faculty,
    get_current_admin,
    get_current_student
)
from app.models.models import (
    User, Student, Subject, BranchSubject, FacultySubject, Faculty, Admin, ClassSession, Attendance
)
from app.schemas.services_schemas.attendance__schemas.attendance_schemas import (
    AttendanceCreateRequest,
    AttendanceResponse,
    AttendanceBulkMarkRequest,
    AttendanceSummaryResponse,
    StudentAttendanceResponse,
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

# =========================================================================
# 1. Mark Single Attendance (Faculty Only)
# =========================================================================
@router.post("/mark", response_model=AttendanceResponse)
def mark_attendance_route(
    data: AttendanceCreateRequest,
    db: Session = Depends(get_db),
    faculty: Faculty = Depends(get_current_faculty)
):
    return mark_attendance_service(db, data, faculty.user_id)


# =========================================================================
# 2. Bulk Mark Attendance (Faculty Only)
# =========================================================================
@router.post("/bulk-mark")
def bulk_mark_attendance_route(
    request: AttendanceBulkMarkRequest,
    db: Session = Depends(get_db),
    faculty: Faculty = Depends(get_current_faculty)
):
    return bulk_mark_attendance_service(db, request, faculty.user_id)


# =========================================================================
# 3. Generate Attendance "Shells" (Admin Only)
# =========================================================================
@router.post("/generate/{class_session_id}")
def generate_attendance_route(
    class_session_id: int,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    # Pass the admin's branch_id directly into the service layer to enforce isolation boundaries
    return generate_attendance_for_session_service(db, class_session_id, enforce_branch_id=admin.branch_id)


# =========================================================================
# 4. Get Report for a Specific Session
# =========================================================================
@router.get("/session/{class_session_id}", response_model=List[AttendanceResponse])
def get_session_attendance_route(
    class_session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "faculty", "super_admin"))
):
    return get_session_attendance_service(db, class_session_id)


# =========================================================================
# 5. Get Student Summary
# =========================================================================
@router.get("/summary/{usn}", response_model=AttendanceSummaryResponse)
def get_student_summary_route(
    usn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student", "admin", "faculty", "super_admin"))
):
    usn_upper = usn.upper()

    # RBAC Data Isolation Check
    if current_user.role == "student":
        # Resolve the student record instantly using your custom dependency shortcut
        student = get_current_student(current_user=current_user, db=db)
        if student.usn.upper() != usn_upper:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own attendance data summary")

    return get_student_summary_service(db, usn_upper)


# =========================================================================
# 6. Get My Attendance — Grouped by Subjects (Student Only)
# =========================================================================
@router.get("/students/me", response_model=List[StudentAttendanceResponse])
def get_my_attendance_route(
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student) # Using clean record resolver from dependencies
):
    db_attendance = (
        db.query(
            Student.usn.label("usn"),
            User.name.label("student_name"),
            Subject.name.label("subject_name"),
            Subject.code.label("subject_code"),
            func.count(ClassSession.id).label("total_sessions"),
            func.sum(case((Attendance.status == 1, 1), else_=0)).label("attended_sessions"),
            (func.sum(case((Attendance.status == 1, 1), else_=0)) * 100.0 / 
             func.nullif(func.count(ClassSession.id), 0)).label("attendance_percentage"),
        )
        .join(Student, Attendance.student_id == Student.id)
        .join(User, Student.user_id == User.id)
        .join(ClassSession, Attendance.class_session_id == ClassSession.id)
        .join(Subject, ClassSession.subject_id == Subject.id)
        .filter(Attendance.student_id == student.id)
        .group_by(Student.usn, User.name, Subject.name, Subject.code)
        .all()
    )

    if not db_attendance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attendance tracking records found for this profile")

    return [StudentAttendanceResponse(**row._asdict()) for row in db_attendance]


# =========================================================================
# 7. Get Student Attendance Summary for a Specific Subject
# =========================================================================
@router.get("/student/{usn}/subject/{subject_code}", response_model=AttendanceSummaryResponse)
def get_student_subject_attendance_route(
    usn: str,
    subject_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student", "admin", "faculty", "super_admin"))
):
    usn = usn.upper()
    subject_code = subject_code.upper()

    # Robust Multi-Role Data Isolation Rules
    if current_user.role == "student":
        student = get_current_student(current_user=current_user, db=db)
        if student.usn.upper() != usn:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Cannot view external student records.")
            
    elif current_user.role == "faculty":
        faculty = get_current_faculty(current_user=current_user, db=db)
        subject = db.query(Subject).filter(Subject.code == subject_code).first()
        if not subject:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target subject not found")
            
        is_assigned = db.query(FacultySubject).filter(
            FacultySubject.faculty_id == faculty.id, 
            FacultySubject.subject_id == subject.id
        ).first()
        if not is_assigned:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. You do not teach this subject course.")
            
    elif current_user.role == "admin":
        admin = get_current_admin(current_user=current_user, db=db)
        target_student = db.query(Student).filter(Student.usn == usn).first()
        if not target_student or target_student.branch_id != admin.branch_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Student falls outside your branch context domain.")

    return get_student_subject_attendance(db, usn, subject_code)