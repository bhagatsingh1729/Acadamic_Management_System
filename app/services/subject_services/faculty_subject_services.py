from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.models import Faculty, FacultySubject, Subject
from app.crud.fundamental_crud.faculty_subject_crud import (
    assign_subject_to_faculty,
)
from app.schemas.fundamental_schemas.faculty_subject_schema import (
    FacultySubjectCreate,
)
from app.schemas.services_schemas.subject_schemas.faculty_subject_schemas import (
    FacultySubjectRequest,
    FacultySubjectResponse,
)

# ==========================================
# ASSIGN SUBJECT TO FACULTY
# ==========================================
def assign_subject_to_faculty_service(db: Session, data: FacultySubjectRequest):
    data.employee_id = data.employee_id.upper()
    data.code = data.code.upper()

    db_faculty = db.query(Faculty).filter(Faculty.employee_id == data.employee_id).first()
    db_subject = db.query(Subject).filter(Subject.code == data.code).first()

    if not db_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty member not found")
    if not db_subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject code not found")
    
    try:
        data_payload = FacultySubjectCreate(
            faculty_id=db_faculty.id,
            subject_id=db_subject.id
        )
        mapping = assign_subject_to_faculty(db=db, data=data_payload)
        db.commit()
        db.refresh(mapping)

        # This endpoint matches FacultySubjectResponse perfectly
        return FacultySubjectResponse(
            employee_id=db_faculty.employee_id,
            subject=db_subject
        )
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="An unexpected error occurred while assigning the subject."
        )


# ==========================================
# GET ALL SUBJECTS FOR A SPECIFIC FACULTY
# ==========================================
def get_subjects_of_faculty_service(employee_id: str, db: Session):
    employee_id = employee_id.upper()

    db_faculty = db.query(Faculty).filter(Faculty.employee_id == employee_id).first()
    if not db_faculty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty member not found")
    
    # Eagerly load the target 'subject' records through the junction table
    mappings = (
        db.query(FacultySubject)
        .filter(FacultySubject.faculty_id == db_faculty.id)
        .options(joinedload(FacultySubject.subject))
        .all()
    )
    
    # FIXED: Extract just the subject objects to satisfy list[SubjectResponse]
    return [m.subject for m in mappings]


# ==========================================
# GET ALL FACULTIES ASSIGNED TO A SUBJECT
# ==========================================
def get_faculties_of_subject_service(subject_code: str, db: Session):
    subject_code = subject_code.upper()

    db_subject = db.query(Subject).filter(Subject.code == subject_code).first()
    if not db_subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    
    # Eagerly load the target 'faculty' records through the junction table
    mappings = (
        db.query(FacultySubject)
        .filter(FacultySubject.subject_id == db_subject.id)
        .options(joinedload(FacultySubject.faculty))
        .all()
    )

    # FIXED: Extract just the faculty objects to satisfy list[FacultyResponse]
    return [m.faculty for m in mappings]


# ==========================================
# REMOVE FACULTY SUBJECT ASSIGNMENT
# ==========================================
def delete_faculty_subject_service(employee_id: str, subject_code: str, db: Session):
    employee_id = employee_id.upper()
    subject_code = subject_code.upper()

    db_faculty = db.query(Faculty).filter(Faculty.employee_id == employee_id).first()
    db_subject = db.query(Subject).filter(Subject.code == subject_code).first()

    if not db_faculty or not db_subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty or Subject does not exist")
    
    mapping = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == db_faculty.id,
        FacultySubject.subject_id == db_subject.id
    ).first()

    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment mapping does not exist")
    
    try:
        db.delete(mapping)
        db.commit()
        return {"message": "Assignment deleted successfully"}
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the mapping."
        )