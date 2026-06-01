from app.schemas.services_schemas.subject_schemas.branch_subject_schemas import (
    BranchSubjectCreateRequest,
    BranchSubjectUpdateRequest,
)
from app.schemas.fundamental_schemas.branch_subject_schema import (
    BranchSubjectCreate,
)
from app.crud.fundamental_crud.branch_subject_crud import (
    assign_subject_to_branch,
    delete_branch_subject,
)

from app.models.models import Branch,Subject,BranchSubject
from sqlalchemy.orm import Session
from fastapi import HTTPException

def assign_subject_to_branch_service(data: BranchSubjectCreateRequest, db: Session):
    data.branch_uid = data.branch_uid.upper()
    data.code = data.code.upper()

    try:
        # Validate existence
        branch = db.query(Branch).filter(Branch.branch_uid == data.branch_uid).first()
        subject = db.query(Subject).filter(Subject.code == data.code).first()

        if not branch or not subject:
            raise HTTPException(status_code=404, detail="Branch or Subject not found")

        # Perform logic
        new_mapping = assign_subject_to_branch(db, branch.id, subject.id)
        
        # COMMIT ONLY ONCE at the end
        db.commit()
        db.refresh(new_mapping)
        return {"message": "Success"}

    except HTTPException:
        db.rollback() # Rollback on validation failure
        raise
    except Exception as e:
        db.rollback() # Rollback on unexpected database errors
        raise HTTPException(status_code=500, detail=str(e))

def get_all_branch_subjects_service(db: Session):
    results = (
        db.query(BranchSubject)
        .join(Branch, Branch.id == BranchSubject.branch_id)
        .join(Subject, Subject.id == BranchSubject.subject_id)
        .with_entities(
            Branch.branch_uid.label("branch_uid"),
            Subject.code.label("code")
        )
        .all()
    )
    return results

    
def get_subjects_of_branch_service(branch_uid: str, db: Session):
    branch_uid = branch_uid.upper()
    results = (
        db.query(BranchSubject)
        .join(Branch, Branch.id == BranchSubject.branch_id)
        .join(Subject, Subject.id == BranchSubject.subject_id)
        .filter(Branch.branch_uid == branch_uid)
        .with_entities(
            Branch.branch_uid.label("branch_uid"),
            Subject.code.label("code")
        )
        .all()
    )
    return results

    
def delete_branch_subject_service(branch_uid: str, subject_code: str, db: Session):
    branch_uid = branch_uid.upper()
    subject_code = subject_code.upper()
    try:
        branch = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
        subject = db.query(Subject).filter(Subject.code == subject_code).first()

        if not branch or not subject:
            raise HTTPException(status_code=404, detail="Branch or Subject not found")

        mapping = db.query(BranchSubject).filter_by(branch_id=branch.id, subject_id=subject.id).first()
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