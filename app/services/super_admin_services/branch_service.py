# =============================================================
# services/super_admin_services/branch_service.py
#
# FIXES APPLIED:
#   FIX 2.4 — create_branch_service uppercase inconsistency
#     Previously: query checked uppercase but created with original case.
#     If "cse" was sent, check passed (no "CSE" found), but record
#     was created as "cse". Then update/delete queries for "CSE" found nothing.
#     Fix: normalize branch_uid to uppercase in data before creating.
# =============================================================

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.services_schemas.super_admin_schemas.branch_schemas import (
    BranchCreate,
    BranchUpdate,
)
from app.models.models import Branch
from app.crud.fundamental_crud.branch_crud import (
    create_branch,
    update_branch,
    get_all_branches,
    get_branch_by_uid,
    delete_branch,
)


def create_branch_service(db: Session, data: BranchCreate):
    # FIX 2.4: normalize to uppercase BEFORE the existence check AND before creation
    # This ensures "cse", "CSE", "Cse" all resolve to the same branch.
    normalized_uid = data.branch_uid.upper()

    branch_exist = db.query(Branch).filter(
        Branch.branch_uid == normalized_uid
    ).first()
    if branch_exist:
        raise HTTPException(status_code=409, detail="Branch already exists")

    # Build a new schema object with the normalized UID
    # so the CRUD receives the consistent uppercase value
    normalized_data = BranchCreate(
        name=data.name,
        branch_uid=normalized_uid
    )
    return create_branch(db, normalized_data)


def update_branch_service(branch_uid: str, data: BranchUpdate, db: Session):
    branch_uid = branch_uid.upper()
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404, detail="Branch not found")

    # If a new branch_uid is being set, normalize it too
    if data.branch_uid:
        data.branch_uid = data.branch_uid.upper()

    return update_branch(branch_id=branch_db.id, branch_data=data, db=db)


def get_all_branches_service(db: Session):
    return get_all_branches(db=db)


def get_branch_via_uid_service(branch_uid: str, db: Session):
    branch_uid = branch_uid.upper()
    branch = get_branch_by_uid(branch_uid=branch_uid, db=db)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


def delete_branch_service(branch_uid: str, db: Session):
    branch_uid = branch_uid.upper()
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404, detail="Branch not found")
    return delete_branch(branch_id=branch_db.id, db=db)
