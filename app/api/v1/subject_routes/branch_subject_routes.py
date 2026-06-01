from app.services.subject_services.branch_subject_services import (
    assign_subject_to_branch_service,
    get_all_branch_subjects_service,
    delete_branch_subject_service,
    get_subjects_of_branch_service,
)
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.dependencies import (
    require_admin,
)

from app.schemas.services_schemas.subject_schemas.branch_subject_schemas import (
    BranchSubjectCreateRequest,
    BranchSubjectUpdateRequest,
    Branch_Subjects_response,
    MappingResponse,
)

from fastapi import HTTPException,Depends,APIRouter

router = APIRouter(prefix="/branch-subjects",tags=["Branch-Subject Mapping"])

@router.post("",response_model=dict)
def assign_subject_service(data:BranchSubjectCreateRequest,db:Session=Depends(get_db)):
    return assign_subject_to_branch_service(data=data,db=db)

@router.get("",response_model=list[MappingResponse])
def get_all_branch_subjects(db:Session=Depends(get_db)):
    return get_all_branch_subjects_service(db=db)

@router.get("/branch/{branch_uid}",response_model=list[MappingResponse])
def get_subjects_of_branch(branch_uid:str,db:Session=Depends(get_db)):
    return get_subjects_of_branch_service(branch_uid=branch_uid,db=db)

@router.delete("/branch/{branch_uid}/subject/{code}")
def delete_branch_subject(branch_uid:str,code:str,db:Session=Depends(get_db)):
    return delete_branch_subject_service(branch_uid=branch_uid,subject_code=code,db=db)
