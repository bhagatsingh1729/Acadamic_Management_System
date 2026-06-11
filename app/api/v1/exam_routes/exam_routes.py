from typing import Optional
from fastapi import HTTPException, Depends, APIRouter, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_super_admin, require_roles
from app.models.models import Student
from app.schemas.services_schemas.exam_schemas.exam_schemas import (
    ExamCreateRequest,
    ExamResponse,
)
from app.schemas.response_schemas.API_Response import ApiResponse

from app.services.exam_services.exam_services import (
    create_exam_service,
    get_all_exams_services,
    delete_exam_service,
)

router = APIRouter(prefix="/exams", tags=["Exam Management"])

# =============================================================
# CREATE EXAM
# =============================================================
@router.post("/create", status_code=status.HTTP_201_CREATED,response_model=ApiResponse[ExamResponse])
def create_exam_route(data: ExamCreateRequest, db: Session = Depends(get_db), current_user = Depends(require_super_admin)):
    """
    Only super admin can create exams.
    """
    result = create_exam_service(db=db, data=data)
    return ApiResponse(success=True,message='Exam created successfully',data=result)


# =============================================================
# GET ALL EXAMS (Unified Endpoint)
# =============================================================
@router.get("", response_model=ApiResponse[list[ExamResponse]])
def get_all_exams_route(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('admin', 'faculty', 'student', 'super_admin'))
):
    """
    Unified function for all roles to get exams.
    If the current user is a student, returns only exams belonging to their semester, batch, and section.
    Otherwise, returns all exams globally.
    """
    student: Optional[Student] = None
    
    if current_user.role == 'student':
        # FIX: Safer query using user_id directly to avoid 'NoneType' 500 error crashes
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Student academic profile configuration not found."
            )

    result = get_all_exams_services(db=db, student=student)
    return ApiResponse(success=True,message='all exams',data=result)


# =============================================================
# DELETE EXAM
# =============================================================
@router.delete("/{exam_id}",response_model=ApiResponse[None])
def delete_exam_route(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('super_admin'))
):
    """
    Only super admin can delete exams.
    """
    delete_exam_service(db=db, exam_id=exam_id)
    return ApiResponse(success=True,message='exam deleted successfully',data=None)