from sqlalchemy.orm import Session
from app.models.models import Branch
from fastapi import HTTPException


from sqlalchemy.orm import Session

from app.models.models import Branch
from app.schemas.branch import BranchCreate, BranchUpdate


def create_branch(db: Session, branch_data: BranchCreate):

    branch = Branch(
        name=branch_data.name,
        branch_uid=branch_data.branch_uid
    )

    db.add(branch)
    db.commit()
    db.refresh(branch)

    return branch


def get_all_branches(db: Session):

    return db.query(Branch).all()


def get_branch_by_id(db: Session, branch_id: int):

    return (
        db.query(Branch)
        .filter(Branch.id == branch_id)
        .first()
    )


def get_branch_by_uid(db: Session, branch_uid: str):

    return (
        db.query(Branch)
        .filter(Branch.branch_uid == branch_uid)
        .first()
    )


def update_branch(
    db: Session,
    branch_id: int,
    branch_data: BranchUpdate
):

    branch = (
        db.query(Branch)
        .filter(Branch.id == branch_id)
        .first()
    )

    if not branch:
        return None

    update_data = branch_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(branch, key, value)

    db.commit()
    db.refresh(branch)

    return branch


def delete_branch(db: Session, branch_id: int):

    branch = (
        db.query(Branch)
        .filter(Branch.id == branch_id)
        .first()
    )

    if not branch:
        return None

    db.delete(branch)
    db.commit()

    return branch




