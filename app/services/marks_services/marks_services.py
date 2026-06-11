from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List

from app.schemas.services_schemas.marks_schemas.marks_schemas import AssignMarksRequest, AssignMarksResponse
from app.schemas.fundamental_schemas.marks_schema import MarksCreate
from app.crud.fundamental_crud.marks_crud import assign_marks
from app.models.models import Student, Exam, StudentSubject, FacultySubject, Marks

def assign_marks_service(db: Session, data: AssignMarksRequest, faculty_id: int) -> AssignMarksResponse:
    target_usn = data.usn.upper()
    
    db_exam = db.query(Exam).filter(Exam.id == data.exam_id).first()
    if not db_exam:
        raise HTTPException(status_code=404, detail='Exam record not found.')
    
    db_student = db.query(Student).filter(Student.usn == target_usn).first()
    if not db_student:
        raise HTTPException(status_code=404, detail=f'Student with USN {target_usn} not found.')
    
    # 1. Enforce Faculty Subject Teaching Assignment Authorization Boundary
    db_faculty_subject = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == faculty_id,
        FacultySubject.subject_id == db_exam.subject_id
    ).first()
    if not db_faculty_subject:
        raise HTTPException(status_code=403, detail='Access Denied. You are not assigned to teach this subject course.')

    # 2. Verify Student Course Core Registration Enrollment
    db_student_subject = db.query(StudentSubject).filter(
        StudentSubject.student_id == db_student.id,
        StudentSubject.subject_id == db_exam.subject_id
    ).first()
    if not db_student_subject:
        raise HTTPException(status_code=400, detail='Student is not enrolled in this specific course subject.')
    
    try:
        data_payload = MarksCreate(student_id=db_student.id, exam_id=db_exam.id, score=data.score)
        marks = assign_marks(db=db, data=data_payload, student=db_student, exam=db_exam)
        db.commit()
        db.refresh(marks)

        return AssignMarksResponse(
            id=marks.id,
            usn=db_student.usn,
            exam_id=db_exam.id,
            subject_code=db_exam.subject.code,
            score=marks.score
        )
    except Exception as e:
        db.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


def update_marks_service(db: Session, usn: str, exam_id: int, score: int, faculty_id: int) -> AssignMarksResponse:
    usn_upper = usn.upper()
    
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        raise HTTPException(status_code=404, detail='Exam record context target not found.')

    # Verify Faculty Authorization to modify entries for this subject course
    is_assigned = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == faculty_id,
        FacultySubject.subject_id == db_exam.subject_id
    ).first()
    if not is_assigned:
        raise HTTPException(status_code=403, detail='Access Denied. Unauthorized to alter details for this course.')

    db_student = db.query(Student).filter(Student.usn == usn_upper).first()
    if not db_student:
        raise HTTPException(status_code=404, detail='Student profile target not found.')
    
    db_marks = db.query(Marks).filter(Marks.student_id == db_student.id, Marks.exam_id == db_exam.id).first()
    if not db_marks:
        raise HTTPException(status_code=404, detail='No existing marks entry found to update for this context.')
    
    if not (0 <= score <= db_exam.max_marks):
        raise HTTPException(status_code=400, detail=f'Invalid score entry bounds. Must rest between 0 and {db_exam.max_marks}.')

    try:
        db_marks.score = score
        db.commit()
        db.refresh(db_marks)
        return AssignMarksResponse(
            id=db_marks.id,
            usn=db_student.usn,
            exam_id=db_exam.id,
            subject_code=db_exam.subject.code,
            score=db_marks.score
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_marks_of_exam_service(db: Session, exam_id: int) -> List[AssignMarksResponse]:
    results = db.query(Marks).filter(Marks.exam_id == exam_id).all()
    return [
        AssignMarksResponse(
            id=m.id,
            usn=m.student.usn,
            exam_id=m.exam_id,
            subject_code=m.exam.subject.code,
            score=m.score
        ) for m in results
    ]


def get_student_marks_service(db: Session, student_usn: str) -> List[AssignMarksResponse]:
    db_student = db.query(Student).filter(Student.usn == student_usn.upper()).first()
    if not db_student:
        raise HTTPException(status_code=404, detail='Student profile not found.')

    results = db.query(Marks).filter(Marks.student_id == db_student.id).all()
    return [
        AssignMarksResponse(
            id=m.id,
            usn=db_student.usn,
            exam_id=m.exam_id,
            subject_code=m.exam.subject.code,
            score=m.score
        ) for m in results
    ]


def delete_marks_service(db: Session, marks_id: int, faculty_id: int) -> bool:
    db_marks = db.query(Marks).filter(Marks.id == marks_id).first()
    if not db_marks:
        raise HTTPException(status_code=404, detail='Target marks record entry not found.')

    # Ensure the faculty deleting the record teaches the associated subject course
    is_authorized = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == faculty_id,
        FacultySubject.subject_id == db_marks.exam.subject_id
    ).first()
    if not is_authorized:
        raise HTTPException(status_code=403, detail='Access Denied. You do not teach the course associated with this entry.')

    try:
        db.delete(db_marks)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))