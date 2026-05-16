


from fastapi import APIRouter,Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.branch import (
    BranchCreate,
    BranchUpdate,
    BranchResponse
)

from app.crud.branch_crud import (
    create_branch,
    get_all_branches,
    get_branch_by_id,
    get_branch_by_uid,
    update_branch,
    delete_branch
)

router = APIRouter(
    prefix="/branches",
    tags=["Branches"]
)


@router.post("/", response_model=BranchResponse)
def create_branch_route(
    branch_data: BranchCreate,
    db: Session = Depends(get_db)
):

    return create_branch(db, branch_data)


@router.get("/", response_model=list[BranchResponse])
def get_all_branches_route(
    db: Session = Depends(get_db)
):

    return get_all_branches(db)


@router.get("/{branch_id}", response_model=BranchResponse)
def get_branch_by_id_route(
    branch_id: int,
    db: Session = Depends(get_db)
):

    branch = get_branch_by_id(db, branch_id)

    if not branch:
        raise HTTPException(
            status_code=404,
            detail="Branch not found"
        )

    return branch


@router.get("/uid/{branch_uid}", response_model=BranchResponse)
def get_branch_by_uid_route(
    branch_uid: str,
    db: Session = Depends(get_db)
):

    branch = get_branch_by_uid(db, branch_uid)

    if not branch:
        raise HTTPException(
            status_code=404,
            detail="Branch not found"
        )

    return branch


@router.put("/{branch_id}", response_model=BranchResponse)
def update_branch_route(
    branch_id: int,
    branch_data: BranchUpdate,
    db: Session = Depends(get_db)
):

    branch = update_branch(
        db,
        branch_id,
        branch_data
    )

    if not branch:
        raise HTTPException(
            status_code=404,
            detail="Branch not found"
        )

    return branch


@router.delete("/{branch_id}")
def delete_branch_route(
    branch_id: int,
    db: Session = Depends(get_db)
):

    branch = delete_branch(db, branch_id)

    if not branch:
        raise HTTPException(
            status_code=404,
            detail="Branch not found"
        )

    return {
        "message": "Branch deleted successfully"
    }