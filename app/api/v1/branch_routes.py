from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Branch
from app.core.dependencies import (
    require_roles,
    require_super_admin,
    get_current_admin,
    get_current_student,
    get_current_user,
)
from app.services.branch_services.branch_service import(
    create_branch_service,
    update_branch_service,
    get_all_branches_service,
    get_branch_via_uid_service,
    delete_branch_service
)
from app.schemas.services_schemas.branch_schema import BranchCreate,BranchResponse,BranchUpdate

router = APIRouter(prefix="/branch", tags=["branch"])

@router.post("/create",response_model=BranchResponse)
def create_branch_route(data:BranchCreate,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return create_branch_service(db=db,data=data)

@router.patch("/{branch_uid}/update",response_model=BranchResponse)
def update_branch_route(branch_uid:str,data:BranchUpdate,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return update_branch_service(branch_uid=branch_uid,data=data,db=db)

@router.get("/all")
def get_all_branch_route(db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return get_all_branches_service(db=db)

@router.get("/{branch_uid}")
def delete_branch_route(branch_uid:str,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return get_branch_via_uid_service(branch_uid=branch_uid,db=db)

@router.delete("/{branch_uid}/delete")
def delete_branch_route(branch_uid:str,db:Session = Depends(get_db),current_user = Depends(require_super_admin)):
    return delete_branch_service(branch_uid=branch_uid,db=db)


