# =========================================================
# class_session_crud.py
# =========================================================

from sqlalchemy.orm import Session

from app.models.models import Faculty, Subject, FacultySubject, Student, ClassSession
from app.schemas.fundamental_schemas.class_session_schema import ClassSessionCreate


def create_class_session(db: Session, session_data: ClassSessionCreate):

    faculty = (
        db.query(Faculty)
        .filter(Faculty.id == session_data.faculty_id)
        .first()
    )

    if not faculty:
        raise ValueError("faculty not found")

    subject = (
        db.query(Subject)
        .filter(Subject.id == session_data.subject_id)
        .first()
    )

    if not subject:
        raise ValueError("subject not found")

    # ✅ semester validation (NEW)
    if subject.semester != session_data.semester:
        raise ValueError("subject semester mismatch with session semester")

    faculty_subject = (
        db.query(FacultySubject)
        .filter(
            FacultySubject.faculty_id == session_data.faculty_id,
            FacultySubject.subject_id == session_data.subject_id
        )
        .first()
    )

    if not faculty_subject:
        raise ValueError("faculty is not assigned to this subject")

    if session_data.end_time <= session_data.start_time:
        raise ValueError("end_time must be greater than start_time")

    students_exist = (
        db.query(Student)
        .filter(
            Student.batch == session_data.batch,
            Student.section == session_data.section,
            Student.semester == session_data.semester   # ✅ FIXED
        )
        .first()
    )

    if not students_exist:
        raise ValueError("no students found for this batch, section, semester")

    existing_session = (
        db.query(ClassSession)
        .filter(
            ClassSession.faculty_id == session_data.faculty_id,
            ClassSession.subject_id == session_data.subject_id,
            ClassSession.date == session_data.date,
            ClassSession.start_time == session_data.start_time,
            ClassSession.section == session_data.section,
            ClassSession.semester == session_data.semester   # ✅ NEW
        )
        .first()
    )

    if existing_session:
        raise ValueError("class session already exists")

    new_session = ClassSession(
        faculty_id=session_data.faculty_id,
        subject_id=session_data.subject_id,

        semester=session_data.semester,

        date=session_data.date,

        start_time=session_data.start_time,
        end_time=session_data.end_time,

        batch=session_data.batch,
        section=session_data.section
    )

    db.add(new_session)
    #db.commit()
    #db.refresh(new_session)

    return new_session


def get_all_class_sessions(db: Session):
    return db.query(ClassSession).all()


def get_class_session_by_id(db: Session, class_session_id: int):

    session = (
        db.query(ClassSession)
        .filter(ClassSession.id == class_session_id)
        .first()
    )

    if not session:
        raise ValueError("class session not found")

    return session


def delete_class_session(db: Session, class_session_id: int):

    session = (
        db.query(ClassSession)
        .filter(ClassSession.id == class_session_id)
        .first()
    )

    if not session:
        raise ValueError("class session not found")

    db.delete(session)
    #db.commit()