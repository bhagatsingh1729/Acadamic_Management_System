# =============================================================
# api/v1/super_admin_routes/branch_routes.py
#
# FIXES APPLIED:
#   FIX 1.5 — Duplicate function name 'delete_branch_route'
#     The GET /{branch_uid} handler was named 'delete_branch_route'
#     which is the same name as the DELETE handler below it.
#     Python kept only the last definition — the GET route was dead.
#     Fixed by renaming the GET handler to 'get_branch_route'.
#
#   ALSO FIXED — Added response_model to GET routes
#     GET /all and GET /{branch_uid} were missing response_model.
#
#   ALSO FIXED — Removed unused imports
#     get_current_admin, get_current_student were imported but never used.
# =============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import require_super_admin
from app.services.super_admin_services.branch_service import (
    create_branch_service,
    update_branch_service,
    get_all_branches_service,
    get_branch_via_uid_service,
    delete_branch_service,
)
from app.schemas.services_schemas.super_admin_schemas.branch_schemas import (
    BranchCreate,
    BranchResponse,
    BranchUpdate,
)

router = APIRouter(prefix="/branch", tags=["Branch"])


@router.post("/create", response_model=BranchResponse)
def create_branch_route(
    data: BranchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return create_branch_service(db=db, data=data)


@router.get("/all", response_model=list[BranchResponse])
def get_all_branch_route(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_branches_service(db=db)


@router.get("/{branch_uid}", response_model=BranchResponse)
def get_branch_route(                           # FIX 1.5: renamed from delete_branch_route
    branch_uid: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_branch_via_uid_service(branch_uid=branch_uid, db=db)


@router.patch("/update/{branch_uid}", response_model=BranchResponse)
def update_branch_route(
    branch_uid: str,
    data: BranchUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return update_branch_service(branch_uid=branch_uid, data=data, db=db)


@router.delete("/delete/{branch_uid}")
def delete_branch_route(                        # this name is now unique
    branch_uid: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return delete_branch_service(branch_uid=branch_uid, db=db)
