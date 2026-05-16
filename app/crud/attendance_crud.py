from sqlalchemy.orm import Session

from app.models.models import Attendance, Student, ClassSession


def create_attendance(db: Session, data):

    student = (
        db.query(Student)
        .filter(Student.id == data.student_id)
        .first()
    )

    if not student:
        raise ValueError("student not found")

    session = (
        db.query(ClassSession)
        .filter(ClassSession.id == data.class_session_id)
        .first()
    )

    if not session:
        raise ValueError("class session not found")

    # prevent duplicate attendance
    existing = (
        db.query(Attendance)
        .filter(
            Attendance.student_id == data.student_id,
            Attendance.class_session_id == data.class_session_id
        )
        .first()
    )

    if existing:
        raise ValueError("attendance already exists")

    if data.status not in [0, 1]:
        raise ValueError("invalid status")

    attendance = Attendance(
        student_id=data.student_id,
        class_session_id=data.class_session_id,
        status=data.status
    )

    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return attendance

def generate_attendance_for_session(db: Session, class_session_id: int):

    session = (
        db.query(ClassSession)
        .filter(ClassSession.id == class_session_id)
        .first()
    )

    if not session:
        raise ValueError("class session not found")

    students = (
        db.query(Student)
        .filter(
            Student.batch == session.batch,
            Student.section == session.section,
            Student.semester == session.semester
        )
        .all()
    )

    attendance_rows = []

    for student in students:

        existing = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == student.id,
                Attendance.class_session_id == session.id
            )
            .first()
        )

        if existing:
            continue

        attendance_rows.append(
            Attendance(
                student_id=student.id,
                class_session_id=session.id,
                status=0
            )
        )

    db.add_all(attendance_rows)
    db.commit()

    return {"message": "attendance generated"}


def get_attendance_by_session(db: Session, class_session_id: int):

    return (
        db.query(Attendance)
        .filter(Attendance.class_session_id == class_session_id)
        .all()
    )

def get_student_attendance(db: Session, student_id: int):

    return (
        db.query(Attendance)
        .filter(Attendance.student_id == student_id)
        .all()
    )

def mark_attendance(db: Session, attendance_id: int, status: int):

    record = (
        db.query(Attendance)
        .filter(Attendance.id == attendance_id)
        .first()
    )

    if not record:
        raise ValueError("attendance not found")

    if status not in [0, 1]:
        raise ValueError("invalid status")

    record.status = status

    db.commit()
    db.refresh(record)

    return record