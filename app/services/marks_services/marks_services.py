from app.schemas.services_schemas.marks_schemas.marks_schemas import (
    AssignMarksRequest,
    AssignMarksResponse,
)
from app.schemas.fundamental_schemas.marks_schema import (
    MarksCreate,
)
from app.crud.fundamental_crud.marks_crud import (
    assign_marks,
    update_marks,
)

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional
from app.models.models import Faculty,FacultySubject,Exam,StudentSubject,Student,Marks,User

def assign_marks_service(data:AssignMarksRequest,db:Session,faculty_id:Optional[int] = None):
    data.usn = data.usn.upper()
    db_exam = db.query(Exam).filter(Exam.id == data.exam_id).first()

    if not db_exam:
        raise HTTPException(status_code=404,detail='Exam not found')
    
    db_student = db.query(Student).filter(Student.usn == data.usn).first()
    
    if not db_student:
        raise HTTPException(status_code=400,detail='student not found')
    
    db_student_subject = db.query(StudentSubject).filter(StudentSubject.student_id == db_student.id,StudentSubject.subject_id == db_exam.subject_id).first()

    if not db_student_subject:
        raise HTTPException(status_code=400,detail='student not enrolled for this subject')
    
    db_faculty_subject = db.query(FacultySubject).filter(FacultySubject.faculty_id == faculty_id,FacultySubject.subject_id == db_exam.subject_id).first()

    if not db_faculty_subject:
        raise HTTPException(status_code=409,detail='you dont teach this subject')
    
    try:
        data_payload = MarksCreate(
            student_id=db_student.id,
            exam_id=db_exam.id,
            score=data.score
        )
        marks = assign_marks(db=db,data=data_payload,student=db_student,exam=db_exam)
        db.commit()
        db.refresh(marks)

        return AssignMarksResponse(
            usn=db_student.usn,
            exam_id=db_exam.id,
            score=data.score
        )
    except HTTPException:
        db.rollback()
        raise

def update_marks_service(score: int, usn: str, exam_id: int, db: Session):
    usn = usn.upper()
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        raise HTTPException(status_code=404, detail='Exam not found')
    
    db_student = db.query(Student).filter(Student.usn == usn).first()
    if not db_student:
        raise HTTPException(status_code=400, detail='Student not found')
    
    # FIX: Corrected comparison
    db_marks = db.query(Marks).filter(
        Marks.student_id == db_student.id, 
        Marks.exam_id == db_exam.id  # <-- Fixed reference
    ).first()

    if not db_marks:
        raise HTTPException(status_code=404, detail='Marks entry not found')
    
    if not (0 <= score <= db_exam.max_marks):
        raise HTTPException(status_code=400, detail='Invalid score')

    try:
        db_marks.score = score
        db.commit()
        db.refresh(db_marks)
        return AssignMarksResponse(usn=db_student.usn, exam_id=db_exam.id, score=db_marks.score)
    except Exception:
        db.rollback()
        raise

def get_marks_of_exam_service(exam_id: int, db: Session):
    results = db.query(Marks).filter(Marks.exam_id == exam_id).all()
    if not results:
        raise HTTPException(status_code=404, detail='No marks found')
        
    # Map to schema here to ensure data consistency
    return [
        AssignMarksResponse(usn=m.student.usn, exam_id=m.exam_id, score=m.score) 
        for m in results
    ]

def get_student_marks_service(student_usn: str, db: Session):
    student_usn = student_usn.upper()
    db_student = db.query(Student).filter(Student.usn == student_usn).first()
    if not db_student:
        raise HTTPException(status_code=404, detail='Student not found')

    # OPTIMIZATION: Removed redundant join since we already have the student ID
    results = db.query(Marks).filter(Marks.student_id == db_student.id).all()

    if not results:
        raise HTTPException(status_code=404, detail='Marks not found')

    return [
        AssignMarksResponse(usn=db_student.usn, exam_id=m.exam_id, score=m.score) 
        for m in results
    ]

def delete_marks_service(marks_id:int,db:Session):
    
    marks = (
        db.query(Marks)
        .filter(Marks.id == marks_id)
        .first()
    )

    if not marks:
        raise HTTPException(
            404,
            "marks not found"
        )

    db.delete(marks)

    db.commit()

    return {
        "message": "marks deleted successfully"
    }