from app.schemas.services_schemas.marks_schemas.marks_schemas import (
    AssignMarksRequest,
    AssignMarksResponse,
)
from app.services.marks_services.marks_services import (
    assign_marks_service,
    update_marks_service,
    get_marks_of_exam_service,
    get_student_marks_service,
)

from app.models.models import Faculty,Exam,Marks,FacultySubject,Subject
from sqlalchemy.orm import Session
from app.core.dependencies import require_roles
from fastapi import HTTPException,Depends,APIRouter
from  app.database import get_db

router = APIRouter(prefix="/marks",tags=['Marks'])

@router.post("/assign",response_model=AssignMarksResponse)
def assign_marks_route(data:AssignMarksRequest,db:Session=Depends(get_db),current_user=Depends(require_roles("faculty"))):

    faculty_id = None

    if current_user.role == 'faculty':
        db_faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        if not db_faculty:
            raise HTTPException(status_code=404,detail='faculty not found')
    
    return assign_marks_service(db=db,data=data,faculty_id=db_faculty.id)

@router.get("/me",response_model=list[AssignMarksResponse])
def students_get_marks_route(db:Session=Depends(get_db),current_user = Depends(require_roles("student"))):
    db_marks = db.query(Marks).filter(Marks.student_id == current_user.student.id).all()

    if not db_marks:
        raise HTTPException(status_code=404,detail='no marks found')
    
    return [
        AssignMarksResponse(
            id=row.id,
            usn=row.student.usn,
            exam_id=row.exam.id,
            subject_code = row.exam.subject.code,
            score=row.score
        )for row in db_marks
    ]


@router.get("/{exam_id}",response_model=list[AssignMarksResponse])
def get_all_exam_marks_route(exam_id:int,db:Session=Depends(get_db),current_user=Depends(require_roles("faculty","admin","super_admin"))):

    return get_marks_of_exam_service(db=db,exam_id=exam_id)

@router.get("/students/{usn}",response_model=list[AssignMarksResponse])
def get_student_marks_route(usn:str,db:Session=Depends(get_db),current_user=Depends(require_roles("faculty","admin","super_admin","student"))):

    if current_user.role == "student":
        if current_user.student.usn != usn.upper():
            raise HTTPException(status_code=409,detail='you can view only your marks')
    
    return get_student_marks_service(db=db,student_usn=usn)

@router.patch("/student/{usn}/exam/{exam_id}", response_model=AssignMarksResponse)
def update_student_marks(
    usn: str, 
    exam_id: int, 
    score: int, # Add this so you receive the data
    db: Session = Depends(get_db), 
    current_user = Depends(require_roles("faculty"))
):
    # 1. Fetch Exam first
    db_exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not db_exam:
        raise HTTPException(status_code=404, detail='Exam not found')
    
    # 2. Authorization check
    db_faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
    db_faculty_subject = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == db_faculty.id,
        FacultySubject.subject_id == db_exam.subject_id
    ).first()

    if not db_faculty_subject:
        raise HTTPException(status_code=403, detail='Unauthorized to update this subject')
        
    return update_marks_service(db=db, usn=usn, exam_id=exam_id, score=score)

@router.delete("/delete/{marks_id}")
def delete_marks_route(
    marks_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_roles("faculty"))
):
    db_marks = db.query(Marks).filter(Marks.id == marks_id).first()
    if not db_marks:
        raise HTTPException(status_code=404, detail='Marks not found')
    
    # Authorization logic
    db_exam = db.query(Exam).filter(Exam.id == db_marks.exam_id).first() # FIX: match correct ID
    db_faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
    
    # Check if faculty teaches the subject of that exam
    is_authorized = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == db_faculty.id,
        FacultySubject.subject_id == db_exam.subject_id
    ).first()

    if not is_authorized:
        raise HTTPException(status_code=403, detail='Unauthorized')
            
    db.delete(db_marks)
    db.commit()

    return {
        "message": "marks deleted successfully"
    }