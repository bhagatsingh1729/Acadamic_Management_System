import logging
from datetime import date
from typing import List, Optional, Literal
from fastapi import HTTPException, status
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from app.schemas.fundamental_schemas.class_session_schema import ClassSessionCreate
from app.schemas.services_schemas.class_session_schemas.class_session_schemas import (
    ClassSessionCreateRequest,
    ClassSessionResponse,
)
from app.crud.fundamental_crud.class_session_crud import (
    create_class_session,
    delete_class_session,
)
from app.models.models import ClassSession, Faculty, Subject, User, BranchSubject, Student, StudentSubject

logger = logging.getLogger(__name__)

# Helper function to inject time-bound sorting filters dynamically
def _apply_timeframe_filter(query, timeframe: Optional[Literal["today", "recent", "upcoming"]]):
    current_date = date.today()
    if timeframe == "today":
        return query.filter(ClassSession.date == current_date).order_by(ClassSession.start_time.asc())
    elif timeframe == "recent":
        return query.filter(ClassSession.date < current_date).order_by(ClassSession.date.desc(), ClassSession.start_time.desc())
    elif timeframe == "upcoming":
        return query.filter(ClassSession.date > current_date).order_by(ClassSession.date.asc(), ClassSession.start_time.asc())
    return query.order_by(ClassSession.date.desc(), ClassSession.start_time.asc())


# =============================================================
# CREATE CLASS SESSION SERVICE
# =============================================================
def create_class_session_service(db: Session, data: ClassSessionCreateRequest, enforce_branch_id: Optional[int] = None):
    data.employee_id = data.employee_id.upper()
    data.code = data.code.upper()
    data.section = data.section.upper()

    if data.start_time >= data.end_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start time must precede end time.")

    # Single unified lookup block for performance
    db_faculty = db.query(Faculty).filter(Faculty.employee_id == data.employee_id).first()
    db_subject = db.query(Subject).filter(Subject.code == data.code).first()

    if not db_faculty or not db_subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty or Subject configuration not found.")

    # Branch authorization boundary enforcement
    if enforce_branch_id is not None:
        subject_branch = db.query(BranchSubject).filter(
            BranchSubject.subject_id == db_subject.id,
            BranchSubject.branch_id == enforce_branch_id
        ).first()
        if not subject_branch:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Subject does not belong to your assigned branch boundaries.")

    # Look for Scheduling Overlaps / Room / Teacher conflicts
    clash_check = db.query(ClassSession).filter(
        ClassSession.date == data.date,
        or_(
            ClassSession.faculty_id == db_faculty.id,
            and_(
                ClassSession.batch == data.batch,
                ClassSession.semester == data.semester,
                ClassSession.section == data.section
            )
        ),
        ClassSession.start_time < data.end_time,
        ClassSession.end_time > data.start_time
    ).first()

    if clash_check:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Scheduling Conflict: This instructor or student section cohort is already booked for this time."
        )
    
    try:
        data_payload = ClassSessionCreate(
            faculty_id=db_faculty.id,
            subject_id=db_subject.id,
            semester=data.semester,
            date=data.date,
            start_time=data.start_time,
            end_time=data.end_time,
            batch=data.batch,
            section=data.section
        )
        class_session = create_class_session(db=db, session_data=data_payload)
        db.commit()
        db.refresh(class_session)
        return {"message": "Class session created successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during creation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to persist class session layout.")


# =============================================================
# GET STUDENT CLASS SESSION SERVICE
# =============================================================
def get_student_classes_service(db: Session, user_id: int, timeframe: Optional[str] = None) -> List[ClassSessionResponse]:
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student structural profile missing.")

    query = (
        db.query(ClassSession)
        .join(StudentSubject, ClassSession.subject_id == StudentSubject.subject_id)
        .join(Faculty, Faculty.id == ClassSession.faculty_id)
        .join(Student, StudentSubject.student_id == Student.id)
        .join(Subject, Subject.id == ClassSession.subject_id)
        .join(User, Faculty.user_id == User.id)
        .filter(
            Student.id == student.id,
            ClassSession.semester == student.semester,
            ClassSession.batch == student.batch,
            ClassSession.section == student.section
        )
    )

    query = _apply_timeframe_filter(query, timeframe)
    results = query.with_entities(
        ClassSession.id.label("session_id"),
        User.name.label("faculty_name"),
        Faculty.employee_id.label("employee_id"),
        Subject.code.label("code"),
        ClassSession.semester,
        ClassSession.date,
        ClassSession.start_time,
        ClassSession.end_time,
        ClassSession.batch,
        ClassSession.section
    ).all()

    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No scheduled classes matching criteria found.")

    return [ClassSessionResponse(**session._asdict()) for session in results]


# =============================================================
# GET ALL CLASS SESSIONS SERVICE (ADMIN / GLOBAL)
# =============================================================
def get_all_class_session_service(db: Session, enforced_branch_id: Optional[int] = None, timeframe: Optional[str] = None) -> List[ClassSessionResponse]:
    query = (
        db.query(ClassSession)
        .join(Faculty, ClassSession.faculty_id == Faculty.id)
        .join(User, Faculty.user_id == User.id)
        .join(Subject, ClassSession.subject_id == Subject.id)
    )

    if enforced_branch_id:
        query = query.join(BranchSubject, Subject.id == BranchSubject.subject_id).filter(BranchSubject.branch_id == enforced_branch_id)

    query = _apply_timeframe_filter(query, timeframe)
    results = query.with_entities(
        ClassSession.id.label("session_id"),
        User.name.label("faculty_name"),
        Faculty.employee_id.label("employee_id"),
        Subject.code.label("code"),
        ClassSession.semester,
        ClassSession.date,
        ClassSession.start_time,
        ClassSession.end_time,
        ClassSession.batch,
        ClassSession.section
    ).all()

    return [ClassSessionResponse(**session._asdict()) for session in results]


# =============================================================
# GET CLASS SESSIONS FOR SPECIFIC FACULTY BY EMPLOYEE ID
# =============================================================
def get_class_session_of_faculty_service(db: Session, employee_id: str, timeframe: Optional[str] = None) -> List[ClassSessionResponse]:
    query = (
        db.query(ClassSession)
        .join(Faculty, ClassSession.faculty_id == Faculty.id)
        .join(User, Faculty.user_id == User.id)
        .join(Subject, ClassSession.subject_id == Subject.id)
        .filter(Faculty.employee_id == employee_id.upper())
    )

    query = _apply_timeframe_filter(query, timeframe)
    results = query.with_entities(
        ClassSession.id.label("session_id"),
        User.name.label("faculty_name"),
        Faculty.employee_id.label("employee_id"),
        Subject.code.label("code"),
        ClassSession.semester,
        ClassSession.date,
        ClassSession.start_time,
        ClassSession.end_time,
        ClassSession.batch,
        ClassSession.section
    ).all()

    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No class records assigned to this faculty target.")
    
    return [ClassSessionResponse(**session._asdict()) for session in results]


# =============================================================
# DELETE CLASS SESSION SERVICE
# =============================================================
def delete_class_session_service(db: Session, class_session_id: int, enforce_branch_id: Optional[int] = None):
    class_session = db.query(ClassSession).filter(ClassSession.id == class_session_id).first()
    if not class_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target class session instance not found.")
    
    if enforce_branch_id is not None:
        subject_branch = db.query(BranchSubject).filter(
            BranchSubject.subject_id == class_session.subject_id,
            BranchSubject.branch_id == enforce_branch_id
        ).first()
        if not subject_branch:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Cannot alter data rows outside your branch workspace.")

    try:
        delete_class_session(db=db, class_session=class_session)
        db.commit()
        return {"message": "Successfully deleted class session execution row."}
    except Exception as e:
        db.rollback()
        logger.error(f"Deletion crash footprint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to drop operational database context entity.")