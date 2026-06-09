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
from sqlalchemy.orm import Session
from fastapi import APIRouter,HTTPException,Depends

router = APIRouter(prefix="/subjects",tags=["Subject management"])

@router.post("/create",response_model=SubjectResponse)
def create_subject_routes(Subject_data:SubjectCreateRequest,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return create_subject_service(subject_data=Subject_data,db=db)

@router.get("/students/me",response_model=list[SubjectResponse])
def get_my_subjects_student_route(db:Session=Depends(get_db),current_user=Depends(require_roles('student'))):
    if current_user.role == 'student':
        db_enrollments = (
            db.query(StudentSubject)
            .filter(current_user.student.id == StudentSubject.student_id)
        ).all()
        if not db_enrollments:
            raise HTTPException(status_code=404,detail='subjects not found for you')
        return [
            SubjectResponse(
                id=row.subject.id,
                name=row.subject.name,
                code=row.subject.code,
                semester=row.subject.semester,
                credits=row.subject.credits
            )for row in db_enrollments
        ]
    
@router.get("/faculty/me",response_model=list[SubjectResponse])
def get_my_subjects_faculty_route(db:Session=Depends(get_db),current_user=Depends(require_roles('faculty'))):
    if current_user.role == 'faculty':
        db_faculty_subject = (
            db.query(FacultySubject)
            .filter(current_user.faculty.id == FacultySubject.faculty_id)
        ).all()
        if not db_faculty_subject:
            raise HTTPException(status_code=404,detail='subjects not found for you')
        return [
            SubjectResponse(
                id=row.subject.id,
                name=row.subject.name,
                code=row.subject.code,
                semester=row.subject.semester,
                credits=row.subject.credits
            )for row in db_faculty_subject
        ]

@router.get("",response_model=list[SubjectResponse])
def get_all_subjects_route(db:Session=Depends(get_db),current_user=Depends(require_roles("admin","super_admin","hod"))):
    
    if current_user.role == "admin":
        return get_all_subjects_service(db=db,enforced_branch_id=current_user.admin.branch_id)

    return get_all_subjects_service(db=db,enforced_branch_id=None)

@router.get("/{code}",response_model=SubjectResponse)
def get_subject_via_code_route(code:str,db:Session=Depends(get_db),current_user=Depends(require_roles("admin","super_admin","faculty","hod"))):
    return get_subject_via_code_service(code=code,db=db)

@router.patch("/{code}",response_model=SubjectResponse)
def update_subject_route(code:str,subject_data:SubjectUpdateRequest,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return update_subject_service(code=code,subject_data=subject_data,db=db)

@router.delete("/{code}")
def delete_subject_route(code:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return delete_subject_service(code=code,db=db)