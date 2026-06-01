from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import (
    Branch,
    Subject,
    BranchSubject
)

from app.schemas.fundamental_schemas.branch_subject_schema import BranchSubjectCreate

# =========================
# ASSIGN SUBJECT TO BRANCH
# =========================
def assign_subject_to_branch(
    db: Session,
    branch_id:int,
    subject_id:int
):
    # Check duplicate
    if db.query(BranchSubject).filter_by(branch_id=branch_id, subject_id=subject_id).first():
        raise HTTPException(status_code=400, detail="Already assigned")
    
    new_mapping = BranchSubject(branch_id=branch_id, subject_id=subject_id)
    db.add(new_mapping)
    return new_mapping


# =========================
# GET ALL MAPPINGS
# =========================
def get_all_branch_subjects(db: Session):

    mappings = db.query(BranchSubject).all()

    return mappings


# =========================
# GET SUBJECTS OF BRANCH
# =========================
def get_subjects_of_branch(
    db: Session,
    branch_id: int
):

    branch = (
        db.query(Branch)
        .filter(Branch.id == branch_id)
        .first()
    )

    if not branch:
        raise HTTPException(
            status_code=404,
            detail="branch not found"
        )

    return branch.subjects


# =========================
# GET BRANCHES OF SUBJECT
# =========================
def get_branches_of_subject(
    db: Session,
    subject_id: int
):

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    return subject.branches


# =========================
# DELETE MAPPING
# =========================
def delete_branch_subject(
    db: Session,
    mapping_id: int
):

    mapping = (
        db.query(BranchSubject)
        .filter(BranchSubject.id == mapping_id)
        .first()
    )

    if not mapping:
        raise HTTPException(
            status_code=404,
            detail="mapping not found"
        )

    db.delete(mapping)

    db.commit()

    return {
        "message": "mapping deleted successfully"
    }