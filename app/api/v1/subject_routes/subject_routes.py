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
    require_super_admin
)

from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter,HTTPException,Depends

router = APIRouter(prefix="/subjects",tags=["Subject management"])

@router.post("/create",response_model=SubjectResponse)
def create_subject_routes(Subject_data:SubjectCreateRequest,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return create_subject_service(subject_data=Subject_data,db=db)

@router.get("",response_model=list[SubjectResponse])
def get_all_subjects_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_subjects_service(db=db)

@router.get("/{code}",response_model=SubjectResponse)
def get_subject_via_code_route(code:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_subject_via_code_service(code=code,db=db)

@router.patch("/{code}",response_model=SubjectResponse)
def update_subject_route(code:str,subject_data:SubjectUpdateRequest,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return update_subject_service(code=code,subject_data=subject_data,db=db)

@router.delete("/{code}")
def delete_subject_route(code:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return delete_subject_service(code=code,db=db)