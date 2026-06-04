from app.schemas.fundamental_schemas.exam_schema import (
    ExamCreate,
)
from app.schemas.services_schemas.exam_schemas.exam_schemas import (
    ExamCreateRequest,
    ExamResponse,
)
from app.crud.fundamental_crud.exam_crud import (
    create_exam,
)

from typing import Optional
from sqlalchemy.orm import Session
from app.models.models import Exam,Subject,StudentSubject,Student
from fastapi import HTTPException

def create_exam_service(data:ExamCreateRequest,db:Session):
    data.subject_code = data.subject_code.upper()
    db_subject = db.query(Subject).filter(Subject.code == data.subject_code).first()

    if not db_subject:
        raise HTTPException(status_code=404,detail='subject not found')
    
    if db_subject.semester != data.semester:
        raise HTTPException(status_code=400,detail='subject does not belong to semester')
    
    data_payload = ExamCreate(
        type=data.type,
        subject_id=db_subject.id,
        max_marks=data.max_marks,
        semester=db_subject.semester,
        batch=data.batch,
        date=data.date
    )
    try:
        exam = create_exam(data=data_payload,db=db)

        db.commit()
        db.refresh(exam)

        return {'massage':'Exam created successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=str(e))


from sqlalchemy import func

def get_all_exams_services(db: Session, student: Optional[Student] = None):
    # Base query
    query = (
        db.query(Exam)
        .join(Subject, Subject.id == Exam.subject_id)
        .with_entities(
            Exam.type,
            func.upper(Subject.code).label("subject_code"),
            Exam.max_marks,
            Exam.semester,
            Exam.batch,
            Exam.date
        )
    )

    # Apply conditional filter if a student is provided
    if student:
        query = query.join(
            StudentSubject, StudentSubject.subject_id == Exam.subject_id
        ).filter(
            Exam.semester == student.semester,
            StudentSubject.student_id == student.id
        )
    
    results = query.all()

    # Handle empty results
    if student is not None and not results:
        raise HTTPException(status_code=404, detail='No exams found for your profile')

    return [
        ExamResponse(
            type=row.type,
            subject_code=row.subject_code,
            max_marks=row.max_marks,
            semester=row.semester,
            batch=row.batch,
            date=row.date
        ) for row in results
    ]

def delete_exam_service(exam_id:int,db:Session):
    exam_db = db.query(Exam).filter(Exam.id == exam_id).first()

    if not exam_db:
        raise HTTPException(status_code=404,detail='exam not found')
    
    try:
        db.delete(exam_db)
        db.commit()
        return {'message':'successfully deleted'}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,detail=str(e))