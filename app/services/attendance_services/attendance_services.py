from app.crud.fundamental_crud.attendance_crud import (
    create_attendance,
    mark_attendance,
    generate_attendance_for_session,
    get_attendance_by_session,
)
from app.schemas.fundamental_schemas.attendance_schema import (
    AttendanceCreate,
)
from app.schemas.services_schemas.attendance__schemas.attendance_schemas import (
    AttendanceCreateRequest,
    AttendanceResponse,
    BulkAttendanceItem,
    AttendanceBulkMarkRequest,
    AttendanceSummaryResponse,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from app.models.models import Student, ClassSession, Subject, Branch,BranchSubject, Faculty,Attendance,User,StudentSubject


def mark_attendance_service(db: Session, data: AttendanceCreateRequest, faculty_user_id: int):
    # 1. Convert string status to integer
    status_map = {"present": 1, "absent": 0}
    status_val = status_map.get(data.status)
    if status_val is None:
        raise HTTPException(status_code=400, detail="Invalid status value")

    # 2. Get the Student by USN
    data.usn = data.usn.upper()
    student = db.query(Student).filter(Student.usn == data.usn).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # 3. Get the Class Session and verify Faculty permissions
    session = db.query(ClassSession).filter(ClassSession.id == data.class_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Class session not found")

    faculty = db.query(Faculty).filter(Faculty.user_id == faculty_user_id).first()
    if not faculty or session.faculty_id != faculty.id:
        raise HTTPException(status_code=403, detail="You are not authorized to mark attendance for this session")

    # 4. Check/Create Attendance Record
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

        # Fetch extra details for response
        student = db.query(Student).filter(Student.id == record.student_id).join(User).first()
        session = db.query(ClassSession).filter(ClassSession.id == record.class_session_id).join(Subject).first()

        return AttendanceResponse(
            student_name=student.user.name,
            usn=student.usn,
            class_session_id=record.class_session_id,
            subject_name=session.subject.name,
            status="present" if record.status == 1 else "absent"
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_session_attendance_service(db: Session, class_session_id: int):
    # Join with Student, User, and Subject to get the student's name
    results = (
        db.query(Attendance)
        .join(Student, Attendance.student_id == Student.id)
        .join(User, Student.user_id == User.id) # Linking Student to the User table
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

    # Map the status integer back to 'present'/'absent' string for the schema
    return [
        AttendanceResponse(
            student_name=row.student_name,
            usn=row.usn,
            class_session_id=row.class_session_id,
            subject_name=row.subject_name,
            status="present" if row.status == 1 else "absent"
        ) for row in results
    ]

def generate_attendance_for_session_service(db: Session, class_session_id: int):
    try:
        generate_attendance_for_session(db, class_session_id)
        return {"message": "Attendance generated for session"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
def get_attendance_by_session_service(db: Session, class_session_id: int):
    try:
        return get_attendance_by_session(db, class_session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def bulk_mark_attendance_service(db: Session, request: AttendanceBulkMarkRequest, faculty_user_id: int):
    status_map = {"present": 1, "absent": 0}
    session = db.query(ClassSession).filter(ClassSession.id == request.class_session_id).first()
    
    if not session or session.faculty_id != db.query(Faculty).filter(Faculty.user_id == faculty_user_id).first().id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    for record in request.records:
        record.usn = record.usn.upper()
        student = db.query(Student).filter(Student.usn == record.usn).first()

        if not student: 
            continue 

        attendance = db.query(Attendance).filter_by(
            student_id=student.id, class_session_id=session.id
        ).first()

        if attendance:
            attendance.status = status_map[record.status]
        else:
            db.add(Attendance(student_id=student.id, class_session_id=session.id, status=status_map[record.status]))
    
    db.commit()
    return {"message": "Bulk update successful"}

def get_student_summary_service(db: Session, student_usn: str):
    student_usn = student_usn.upper()
    db_student = db.query(Student).filter(Student.usn == student_usn).first()
    if not db_student:
        raise HTTPException(status_code=404, detail='Student not found')
        
    # Use db_student.id, not student_usn
    total = db.query(Attendance).filter(Attendance.student_id == db_student.id).count()
    attended = db.query(Attendance).filter(Attendance.student_id == db_student.id, Attendance.status == 1).count()
    
    percentage = (attended / total * 100) if total > 0 else 0.0
    
    return AttendanceSummaryResponse(
        usn=db_student.usn,
        student_name=db_student.user.name,
        total_sessions=total,
        attended_sessions=attended,
        attendance_percentage=round(percentage, 2)
    )

def get_student_subject_attendance(db:Session,student_usn:str,subject_code:str):
    student_usn = student_usn.upper()
    student_db = db.query(Student).filter(Student.usn == student_usn).first()

    if not student_db:
        raise HTTPException(status_code=404,detail='student does not exist')
    
    subject_code = subject_code.upper()
    subject_db = db.query(Subject).filter(Subject.code == subject_code).first()

    if not subject_db:
        raise HTTPException(status_code=404,detail='subject does not exist')
    
    student_subject_db = db.query(StudentSubject).filter(StudentSubject.student_id == student_db.id,StudentSubject.subject_id == subject_db.id).first()
    if not student_subject_db:
        raise HTTPException(status_code=404,detail='student is not enrolled to this subject')

    query = (
        db.query(Attendance)
        .join(ClassSession, ClassSession.id == Attendance.class_session_id)
        .join(Student, Student.id == Attendance.student_id)
        .join(User, Student.user_id == User.id)
        .filter(ClassSession.subject_id == subject_db.id, Attendance.student_id == student_db.id)
        .with_entities(
            User.name.label("student_name"),
            Student.usn.label("usn"),
            ClassSession.id.label("class_session_id"),
            ClassSession.date.label("date"),
            Attendance.status.label("status")
        )
    ).all()

    count_total = len(query)
    count_attended = sum(1 for record in query if record.status == 1)
    attendance_percentage = (count_attended / count_total * 100) if count_total > 0 else 0.0

    return [
        AttendanceSummaryResponse(
            usn=record.usn,
            student_name=record.student_name,
            total_sessions=count_total,
            attended_sessions=count_attended,
            attendance_percentage=round(attendance_percentage, 2)
        ) for record in query
    ]