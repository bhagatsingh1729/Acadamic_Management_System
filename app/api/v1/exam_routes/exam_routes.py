from app.services.exam_services.exam_services import (
    create_exam_service,
    get_all_exams_services,
    delete_exam_service,
)
from app.schemas.services_schemas.exam_schemas.exam_schemas import (
    ExamCreateRequest,
    ExamResponse,
)

from fastapi import HTTPException,Depends,APIRouter
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.dependencies import require_super_admin,require_roles
from app.models.models import Student,Exam
from typing import Optional

router = APIRouter(prefix="/exams",tags=["Exam Management"])

@router.post("/create")
def create_exam_route(data:ExamCreateRequest,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return create_exam_service(db=db,data=data)


@router.get("", response_model=list[ExamResponse])
def get_all_exams_route(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('admin', 'faculty', 'student', 'super_admin'))
):
    student: Optional[Student] = None
    
    if current_user.role == 'student':
        student = db.query(Student).filter(Student.id == current_user.student.id).first()
        if not student:
            raise HTTPException(status_code=404, detail='Student profile not found')

    return get_all_exams_services(db=db, student=student)

@router.delete("/{exam_id}")
def delete_exam_route(
    exam_id:int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('super_admin'))
):
    return delete_exam_service(db=db,exam_id=exam_id)