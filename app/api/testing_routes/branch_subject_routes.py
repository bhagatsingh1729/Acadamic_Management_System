from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.branch_subject_schema import (
    BranchSubjectCreate
)

from app.crud.fundamental_crud.branch_subject_crud import (
    assign_subject_to_branch,
    get_all_branch_subjects,
    get_subjects_of_branch,
    get_branches_of_subject,
    delete_branch_subject
)


router = APIRouter(
    prefix="/branch-subject",
    tags=["Branch Subject"]
)


# =========================
# ASSIGN SUBJECT TO BRANCH
# =========================
@router.post("/")
def assign_subject_to_branch_route(
    data: BranchSubjectCreate,
    db: Session = Depends(get_db)
):

    return assign_subject_to_branch(
        db,
        data
    )


# =========================
# GET ALL MAPPINGS
# =========================
@router.get("/")
def get_all_branch_subjects_route(
    db: Session = Depends(get_db)
):

    return get_all_branch_subjects(db)


# =========================
# GET SUBJECTS OF BRANCH
# =========================
@router.get("/branch/{branch_id}")
def get_subjects_of_branch_route(
    branch_id: int,
    db: Session = Depends(get_db)
):

    return get_subjects_of_branch(
        db,
        branch_id
    )


# =========================
# GET BRANCHES OF SUBJECT
# =========================
@router.get("/subject/{subject_id}")
def get_branches_of_subject_route(
    subject_id: int,
    db: Session = Depends(get_db)
):

    return get_branches_of_subject(
        db,
        subject_id
    )


# =========================
# DELETE MAPPING
# =========================
@router.delete("/{mapping_id}")
def delete_branch_subject_route(
    mapping_id: int,
    db: Session = Depends(get_db)
):

    return delete_branch_subject(
        db,
        mapping_id
    )