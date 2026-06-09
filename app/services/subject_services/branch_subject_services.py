from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from typing import Optional

from app.models.models import Branch, Subject, BranchSubject
from app.schemas.services_schemas.subject_schemas.branch_subject_schemas import (
    BranchSubjectCreateRequest,
    MappingResponse
)
from app.crud.fundamental_crud.branch_subject_crud import (
    assign_subject_to_branch,
)

def assign_subject_to_branch_service(
    data: BranchSubjectCreateRequest,
    db: Session,
    enforced_branch_uid: Optional[str] = None
):
    data.branch_uid = data.branch_uid.upper()
    data.code = data.code.upper()

    if enforced_branch_uid and data.branch_uid != enforced_branch_uid.upper():
        raise HTTPException(status_code=403, detail="You can only assign subjects to your own branch")

    try:
        branch = db.query(Branch).filter(Branch.branch_uid == data.branch_uid).first()
        subject = db.query(Subject).filter(Subject.code == data.code).first()

        if not branch or not subject:
            raise HTTPException(status_code=404, detail="Branch or Subject not found")

        # Assign and commit
        assign_subject_to_branch(db, branch.id, subject.id)
        db.commit()
        
        # Return the full schema using the objects already in memory
        return MappingResponse(
            branch_uid=branch.branch_uid,
            subject=subject
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_all_branch_subjects_service(db: Session):
    # Use joinedload to fetch the whole object instead of flattening it
    results = (
        db.query(BranchSubject)
        .options(
            joinedload(BranchSubject.branch),
            joinedload(BranchSubject.subject)
        )
        .all()
    )
    
    return [
        MappingResponse(
            branch_uid=mapping.branch.branch_uid,
            subject=mapping.subject
        ) for mapping in results
    ]


def get_subjects_of_branch_service(branch_uid: str, db: Session):
    branch_uid = branch_uid.upper()
    results = (
        db.query(BranchSubject)
        .join(Branch, Branch.id == BranchSubject.branch_id)
        .filter(Branch.branch_uid == branch_uid)
        .options(
            joinedload(BranchSubject.branch),
            joinedload(BranchSubject.subject)
        )
        .all()
    )
    
    return [
        MappingResponse(
            branch_uid=mapping.branch.branch_uid,
            subject=mapping.subject
        ) for mapping in results
    ]


def delete_branch_subject_service(
    branch_uid: str,
    subject_code: str,
    db: Session,
    enforced_branch_uid: Optional[str] = None
):
    branch_uid = branch_uid.upper()
    subject_code = subject_code.upper()

    if enforced_branch_uid and branch_uid != enforced_branch_uid.upper():
        raise HTTPException(status_code=403, detail="You can only delete subject mappings for your own branch")

    try:
        branch = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
        subject = db.query(Subject).filter(Subject.code == subject_code).first()

        if not branch or not subject:
            raise HTTPException(status_code=404, detail="Branch or Subject not found")

        mapping = db.query(BranchSubject).filter_by(
            branch_id=branch.id,
            subject_id=subject.id
        ).first()

        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping not found")

        db.delete(mapping)
        db.commit()
        return {"message": "Mapping deleted successfully"}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))