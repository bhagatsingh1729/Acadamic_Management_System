# =========================================================================
# app/services/attendance_services/attendance_services.py
# =========================================================================

from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional

from app.schemas.fundamental_schemas.attendance_schema import AttendanceCreate
from app.schemas.services_schemas.attendance__schemas.attendance_schemas import (
    AttendanceCreateRequest,
    AttendanceResponse,
    AttendanceBulkMarkRequest,
    AttendanceSummaryResponse,
)
from app.crud.fundamental_crud.attendance_crud import (
    create_attendance,
    mark_attendance,
    generate_attendance_for_session,
)
from app.models.models import (
    Student, ClassSession, Subject, Faculty, Attendance, User, StudentSubject, BranchSubject
)

# =========================================================================
# 1. MARK SINGLE ATTENDANCE
# =========================================================================
def mark_attendance_service(db: Session, data: AttendanceCreateRequest, faculty_user_id: int) -> AttendanceResponse:
    status_map = {"present": 1, "absent": 0}
    status_val = status_map.get(data.status.lower())
    if status_val is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value. Use 'present' or 'absent'.")

    # Verify Class Session and check Faculty permission borders immediately
    session = db.query(ClassSession).filter(ClassSession.id == data.class_session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class session not found")

    faculty = db.query(Faculty).filter(Faculty.user_id == faculty_user_id).first()
    if not faculty or session.faculty_id != faculty.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to mark attendance for this session.")

    # Locate Student by USN
    target_usn = data.usn.upper()
    student = db.query(Student).filter(Student.usn == target_usn).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with USN {target_usn} not found.")

    # Guardrail: Is the student part of this session's batch, semester, and section cohort?
    if (student.batch != session.batch or 
        student.semester != session.semester or 
        student.section != session.section):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Student cohort alignment mismatch for this session's batch/semester/section rules."
        )

    # Process save/update operation
    attendance = db.query(Attendance).filter(
        Attendance.student_id == student.id,
        Attendance.class_session_id == session.id
    ).first()

    try:
        if attendance:
            record = mark_attendance(db, attendance.id, status_val)
        else:
            create_data = AttendanceCreate(
                student_id=student.id,
                class_session_id=session.id,
                status=status_val
            )
            record = create_attendance(db, create_data)

        return AttendanceResponse(
            student_name=student.user.name,
            usn=student.usn,
            class_session_id=record.class_session_id,
            subject_name=session.subject.name,
            status="present" if record.status == 1 else "absent"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =========================================================================
# 2. BULK MARK ATTENDANCE (Optimized O(1) Memory Mapping Architecture)
# =========================================================================
def bulk_mark_attendance_service(db: Session, request: AttendanceBulkMarkRequest, faculty_user_id: int):
    status_map = {"present": 1, "absent": 0}
    
    session = db.query(ClassSession).filter(ClassSession.id == request.class_session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class session context not found")
        
    faculty = db.query(Faculty).filter(Faculty.user_id == faculty_user_id).first()
    if not faculty or session.faculty_id != faculty.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized faculty context operation.")

    if not request.records:
        return {"message": "No modification datasets targets received."}

    # Optimization Trip A: Pull down all target students in 1 database pass
    usn_list = [r.usn.upper() for r in request.records]
    students = db.query(Student).filter(
        Student.usn.in_(usn_list),
        Student.batch == session.batch,
        Student.semester == session.semester,
        Student.section == session.section
    ).all()
    student_map = {s.usn: s for s in students}

    # Optimization Trip B: Pull down existing attendance for this session in 1 query
    existing_attendance = db.query(Attendance).filter(Attendance.class_session_id == session.id).all()
    attendance_map = {a.student_id: a for a in existing_attendance}

    try:
        for record in request.records:
            student = student_map.get(record.usn.upper())
            if not student:
                continue  # Drops requests belonging outside this session cohort layout

            target_status = status_map.get(record.status.lower(), 0)
            existing_record = attendance_map.get(student.id)

            if existing_record:
                existing_record.status = target_status
            else:
                db.add(Attendance(
                    student_id=student.id, 
                    class_session_id=session.id, 
                    status=target_status
                ))
        
        db.commit()
        #return {"message": "Bulk attendance updates written successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =========================================================================
# 3. GENERATE ATTENDANCE SHELLS (With Branch Perimeter Security Verification)
# =========================================================================
def generate_attendance_for_session_service(db: Session, class_session_id: int, enforce_branch_id: Optional[int] = None):
    session = db.query(ClassSession).filter(ClassSession.id == class_session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target session not found.")

    # If accessed by an Admin route, verify that the subject belongs to their branch
    if enforce_branch_id is not None:
        branch_check = db.query(BranchSubject).filter(
            BranchSubject.subject_id == session.subject_id,
            BranchSubject.branch_id == enforce_branch_id
        ).first()
        if not branch_check:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access denied. This class session sits outside your admin branch jurisdiction."
            )

    try:
        generate_attendance_for_session(db, class_session_id)
        db.commit()
        #return {"message": "Attendance sheet initialized for session successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# =========================================================================
# 4. GET REPORT FOR A SESSION
# =========================================================================
def get_session_attendance_service(db: Session, class_session_id: int) -> List[AttendanceResponse]:
    results = (
        db.query(Attendance)
        .join(Student, Attendance.student_id == Student.id)
        .join(User, Student.user_id == User.id) 
        .join(ClassSession, Attendance.class_session_id == ClassSession.id)
        .join(Subject, ClassSession.subject_id == Subject.id)
        .filter(Attendance.class_session_id == class_session_id)
        .with_entities(
            User.name.label("student_name"),
            Student.usn.label("usn"),
            Attendance.class_session_id.label("class_session_id"),
            Subject.name.label("subject_name"),
            Attendance.status.label("status")
        )
    ).all()

    return [
        AttendanceResponse(
            student_name=row.student_name,
            usn=row.usn,
            class_session_id=row.class_session_id,
            subject_name=row.subject_name,
            status="present" if row.status == 1 else "absent"
        ) for row in results
    ]


# =========================================================================
# 5. GET GLOBAL STUDENT SUMMARY (Single Aggregate Query Pattern)
# =========================================================================
def get_student_summary_service(db: Session, student_usn: str) -> AttendanceSummaryResponse:
    student = db.query(Student).filter(Student.usn == student_usn.upper()).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student profile not found')
        
    # Single unified select aggregation avoiding multi-pass counts
    stats = db.query(
        func.count(Attendance.id).label("total"),
        func.sum(Attendance.status).label("attended")
    ).filter(Attendance.student_id == student.id).first()

    total = stats.total or 0
    attended = int(stats.attended or 0)
    percentage = (attended / total * 100) if total > 0 else 0.0
    
    return AttendanceSummaryResponse(
        usn=student.usn,
        student_name=student.user.name,
        total_sessions=total,
        attended_sessions=attended,
        attendance_percentage=round(percentage, 2)
    )


# =========================================================================
# 6. GET STUDENT SUBJECT SPECIFIC ATTENDANCE (Fixed Array Row Explosion Bug)
# =========================================================================
def get_student_subject_attendance(db: Session, student_usn: str, subject_code: str) -> AttendanceSummaryResponse:
    student = db.query(Student).filter(Student.usn == student_usn.upper()).first()
    subject = db.query(Subject).filter(Subject.code == subject_code.upper()).first()

    if not student or not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Requested Student or Subject entity code not found.')
    
    # Confirm course registration enrollment profile mapping up front
    enrollment = db.query(StudentSubject).filter(
        StudentSubject.student_id == student.id,
        StudentSubject.subject_id == subject.id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Student is not explicitly enrolled to this subject course.')

    # Execute aggregate stats calculations inside the DB engine directly
    stats = db.query(
        func.count(Attendance.id).label("total"),
        func.sum(Attendance.status).label("attended")
    ).join(ClassSession, ClassSession.id == Attendance.class_session_id)\
     .filter(ClassSession.subject_id == subject.id, Attendance.student_id == student.id).first()

    total_sessions = stats.total or 0
    attended_sessions = int(stats.attended or 0)
    attendance_percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0.0

    # Returns exactly ONE clean flat object as demanded by your return schema definition
    return AttendanceSummaryResponse(
        usn=student.usn,
        student_name=student.user.name,
        total_sessions=total_sessions,
        attended_sessions=attended_sessions,
        attendance_percentage=round(attendance_percentage, 2)
    )