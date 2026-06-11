from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_super_admin
from app.services.branch_services.branch_services import (
    create_branch_service,
    update_branch_service,
    get_all_branches_service,
    get_branch_via_uid_service,
    delete_branch_service,
)
from app.schemas.services_schemas.branch_schemas.branch_schemas import (
    BranchCreate,
    BranchResponse,
    BranchUpdate,
)
from app.schemas.response_schemas.API_Response import ApiResponse

router = APIRouter(prefix="/branch", tags=["Branch"])


@router.post("/create", response_model=ApiResponse[BranchResponse])
def create_branch_route(
    data: BranchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    result = create_branch_service(db=db, data=data)
    return ApiResponse(success=True,message='created branch successfully',data=result)


@router.get("/all", response_model=ApiResponse[list[BranchResponse]])
def get_all_branch_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    result = get_all_branches_service(db=db)
    return ApiResponse(success=True,message='all branches list',data=result)


@router.get("/{branch_uid}", response_model=ApiResponse[BranchResponse])
def get_branch_route(                           
    branch_uid: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    result = get_branch_via_uid_service(branch_uid=branch_uid, db=db)
    return ApiResponse(success=True,message='branch data',data=result)


@router.patch("/update/{branch_uid}", response_model=ApiResponse[BranchResponse])
def update_branch_route(
    branch_uid: str,
    data: BranchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    result = update_branch_service(branch_uid=branch_uid, data=data, db=db)
    return ApiResponse(success=True,message='updated branch successully',data=result)


@router.delete("/delete/{branch_uid}",response_model=ApiResponse[None])
def delete_branch_route(                        # this name is now unique
    branch_uid: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    delete_branch_service(branch_uid=branch_uid, db=db)
    return ApiResponse(success=True,message='branch deleted successfully',data=None)
