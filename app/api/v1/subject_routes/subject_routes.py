from app.schemas.services_schemas.subject_schemas.subject_schemas import (
    SubjectCreateRequest,
    SubjectUpdateRequest,
    SubjectResponse,
)
from app.services.subject_services.subject_services import (
    create_subject_service,
    get_subject_via_code_service,
    update_subject_service,
    delete_subject_service,
    get_all_subjects_service,
)

from app.core.dependencies import (
    require_super_admin,
    require_roles,
)

from app.database import get_db
from app.models.models import StudentSubject,FacultySubject
from sqlalchemy.orm import Session,joinedload
from fastapi import APIRouter,HTTPException,Depends
from app.schemas.response_schemas.API_Response import ApiResponse

router = APIRouter(prefix="/subjects",tags=["Subject management"])

@router.post("/create",response_model=ApiResponse[SubjectResponse])
def create_subject_routes(Subject_data:SubjectCreateRequest,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    result = create_subject_service(subject_data=Subject_data,db=db)
    return ApiResponse(success=True,message='subject created successfully',data=result)

@router.get("/students/me",response_model=ApiResponse[list[SubjectResponse]])
def get_my_subjects_student_route(db:Session=Depends(get_db),current_user=Depends(require_roles('student'))):
    if current_user.role == 'student':
        db_enrollments = (
            db.query(StudentSubject)
            .options(joinedload(StudentSubject.subject))
            .filter(current_user.student.id == StudentSubject.student_id)
        ).all()
        if not db_enrollments:
            raise HTTPException(status_code=404,detail='subjects not found for you')
        result = [
            SubjectResponse(
                id=row.subject.id,
                name=row.subject.name,
                code=row.subject.code,
                semester=row.subject.semester,
                credits=row.subject.credits
            )for row in db_enrollments
        ]
        return ApiResponse(success=True,message="subjects you're enrolled in",data=result)
    
@router.get("/faculty/me",response_model=ApiResponse[list[SubjectResponse]])
def get_my_subjects_faculty_route(db:Session=Depends(get_db),current_user=Depends(require_roles('faculty'))):
    if current_user.role == 'faculty':
        db_faculty_subject = (
            db.query(FacultySubject)
            .options(joinedload(FacultySubject.subject))
            .filter(current_user.faculty.id == FacultySubject.faculty_id)
        ).all()
        if not db_faculty_subject:
            raise HTTPException(status_code=404,detail='subjects not found for you')
        result = [
            SubjectResponse(
                id=row.subject.id,
                name=row.subject.name,
                code=row.subject.code,
                semester=row.subject.semester,
                credits=row.subject.credits
            )for row in db_faculty_subject
        ]
        return ApiResponse(success=True,message='subjects you teach',data=result)

@router.get("",response_model=ApiResponse[list[SubjectResponse]])
def get_all_subjects_route(db:Session=Depends(get_db),current_user=Depends(require_roles("admin","super_admin","hod"))):
    
    enforced_branch_id = None
    if current_user.role == "admin":
        enforced_branch_id = current_user.admin.branch_id

    result = get_all_subjects_service(db=db,enforced_branch_id=enforced_branch_id)
    return ApiResponse(success=True,message='subjects list',data=result)

@router.get("/{code}",response_model=ApiResponse[SubjectResponse])
def get_subject_via_code_route(code:str,db:Session=Depends(get_db),current_user=Depends(require_roles("admin","super_admin","faculty","hod"))):
    result = get_subject_via_code_service(code=code,db=db)
    return ApiResponse(success=True,message='subject for the given code',data=result)

@router.patch("/{code}",response_model=ApiResponse[SubjectResponse])
def update_subject_route(code:str,subject_data:SubjectUpdateRequest,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    result = update_subject_service(code=code,subject_data=subject_data,db=db)
    return ApiResponse(success=True,message='subject updated',data=result)

@router.delete("/{code}",response_model=ApiResponse[None])
def delete_subject_route(code:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    delete_subject_service(code=code,db=db)
    return ApiResponse(success=True,message='subject deleted',data=None)