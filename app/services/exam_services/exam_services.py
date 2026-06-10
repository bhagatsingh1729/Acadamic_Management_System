import logging
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.models import Exam, Student, StudentSubject, Subject
from app.schemas.fundamental_schemas.exam_schema import ExamCreate
from app.schemas.services_schemas.exam_schemas.exam_schemas import (
    ExamCreateRequest,
    ExamResponse,
)
from app.crud.fundamental_crud.exam_crud import create_exam

logger = logging.getLogger(__name__)

# =============================================================
# 1. CREATE EXAM (Updates to save 'section')
# =============================================================
def create_exam_service(data: ExamCreateRequest, db: Session):
    data.subject_code = data.subject_code.upper()
    data.section = data.section.upper()  # Normalize 'a' -> 'A'

    db_subject = db.query(Subject).filter(Subject.code == data.subject_code).first()

    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Subject code not found"
        )
    
    if db_subject.semester != data.semester:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The provided subject does not belong to this semester."
        )
    
    data_payload = ExamCreate(
        type=data.type,
        subject_id=db_subject.id,
        max_marks=data.max_marks,
        semester=db_subject.semester,
        batch=data.batch,
        section=data.section,  # Saved to DB
        date=data.date
    )
    
    try:
        exam = create_exam(data=data_payload, db=db)
        db.commit()
        db.refresh(exam)
        
        return {"message": "Exam created successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create exam. Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred while creating the exam."
        )


# =============================================================
# 2. GET ALL EXAMS (Updates to filter by 'section')
# =============================================================
def get_all_exams_services(db: Session, student: Optional[Student] = None) -> List[ExamResponse]:
    query = db.query(Exam).options(joinedload(Exam.subject))

    if student:
        # Enforcing complete boundary (Semester + Batch + Section)
        query = (
            query.join(StudentSubject, StudentSubject.subject_id == Exam.subject_id)
            .filter(
                Exam.semester == student.semester,
                Exam.batch == student.batch,
                Exam.section == student.section.upper(),  # Section match enforced
                StudentSubject.student_id == student.id
            )
        )
    
    results = query.all()

    return [
        ExamResponse(
            type=exam.type,
            subject_code=exam.subject.code,
            max_marks=exam.max_marks,
            semester=exam.semester,
            batch=exam.batch,
            section=exam.section,  # Sent back to frontend
            date=exam.date
        ) for exam in results
    ]


# =============================================================
# 3. DELETE EXAM (Stays the same - searches directly by unique ID)
# =============================================================
def delete_exam_service(exam_id: int, db: Session):
    exam_db = db.query(Exam).filter(Exam.id == exam_id).first()

    if not exam_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Exam record not found"
        )
    
    try:
        db.delete(exam_db)
        db.commit()
        return {"message": "Exam deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete exam ID {exam_id}. Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing your deletion request."
        )