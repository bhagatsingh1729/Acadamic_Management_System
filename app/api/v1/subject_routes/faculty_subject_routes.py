from app.services.subject_services.faculty_subject_services import (
    assign_subject_to_faculty_service,
    get_faculties_of_subject_service,
    get_subjects_of_faculty_service,
    delete_faculty_subject_service,
)

from app.schemas.services_schemas.subject_schemas.faculty_subject_schemas import (
    FacultySubjectRequest,
    FacultySubjectResponse,
)

from app.schemas.services_schemas.role_management_schemas.faculty_schemas import (
    FacultyResponse,
)
from sqlalchemy.orm import Session
from fastapi import APIRouter,HTTPException,Depends
from app.core.dependencies import (
    require_super_admin,
    require_roles,
)
from app.schemas.services_schemas.subject_schemas.subject_schemas import (
    SubjectResponse,
)
from app.schemas.response_schemas.API_Response import ApiResponse
from app.database import get_db

router = APIRouter(prefix="/faculty-subjects",tags=['Faculty_Subject Management'])

@router.post("/assign",response_model=ApiResponse[FacultySubjectResponse])
def assign_faculty_subject_route(data:FacultySubjectRequest,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    result = assign_subject_to_faculty_service(db=db,data=data)
    return ApiResponse(success=True,message='successfully assigned subject to faculty',data=result)

@router.get("/subjects/{employee_id}",response_model=ApiResponse[list[SubjectResponse]])
def get_subjects_of_faculty_route(employee_id:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    result = get_subjects_of_faculty_service(db=db,employee_id=employee_id)
    return ApiResponse(success=True,message='subjects list of faculty',data=result)

@router.get("/faculties/{subject_code}",response_model=ApiResponse[list[FacultyResponse]])
def get_faculties_of_subject_route(subject_code:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    result = get_faculties_of_subject_service(db=db,subject_code=subject_code)
    return ApiResponse(success=True,message='list of faculties who teach this subject',data=result)

@router.delete("/delete/{employee_id}/subject/{subject_code}",response_model=ApiResponse[None])
def delete_faculty_subject_route(employee_id:str,subject_code:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    delete_faculty_subject_service(db=db,employee_id=employee_id,subject_code=subject_code)
    return ApiResponse(success=True,message='mapping deleted successfully',data=None)