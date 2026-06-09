from app.schemas.services_schemas.subject_schemas.subject_schemas import (
    SubjectCreateRequest,
    SubjectUpdateRequest,
    SubjectResponse,
)

from app.crud.fundamental_crud.subject_crud import (
    create_subject,
    get_subject_by_code,
    get_subjects_by_semester,
)

from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.models import Subject,Branch,BranchSubject

def create_subject_service(subject_data:SubjectCreateRequest,db:Session):
    try:
        new_subject = create_subject(db=db,subject_data=subject_data)
        db.commit()
        db.refresh(new_subject)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400,detail=f'exception {str(e)}')
    

def get_subject_via_code_service(code:str,db:Session):
    code = code.upper()
    return get_subject_by_code(db=db,subject_code=code)

def get_all_subjects_service(db:Session,enforced_branch_id:Optional[int] = None):
    try:
        if enforced_branch_id:
            db_subjects = (
                db.query(BranchSubject)
                .filter(enforced_branch_id == BranchSubject.branch_id)
            ).all()

            if not db_subjects:
                raise HTTPException(status_code=404,detail='subject not found for your branch')
            return [
                SubjectResponse(
                    id=row.subject.id,
                    name=row.subject.name,
                    code=row.subject.code,
                    semester=row.subject.semester,
                    credits=row.subject.credits
                )for row in db_subjects
            ]

        db_subjects = db.query(Subject).all()
        return db_subjects
    except HTTPException:
        raise HTTPException(status_code=404,detail='no subject found')
    
def get_subject_via_sem_service(sem:int,db:Session):
    try:
        return get_subjects_by_semester(db,sem)
    except HTTPException:
        raise

def update_subject_service(
    code: str,
    subject_data: SubjectUpdateRequest,
    db: Session
):
    # normalize lookup code
    code = code.upper()
    db_subject = db.query(Subject).filter(Subject.code == code).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # dump only provided fields
    update_data = subject_data.model_dump(exclude_unset=True)

    # normalization rules
    normalizers = {
        "code": str.upper,   # always uppercase
        "name": lambda v: v, # keep as-is (or str.upper if you want names uppercase too)
    }

    # apply normalization safely
    for field, transform in normalizers.items():
        value = update_data.get(field)
        if value is not None:
            update_data[field] = transform(value)

    # apply updates safely
    for key, value in update_data.items():
        if value is not None:   # skip None values
            setattr(db_subject, key, value)

    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject_service(code:str,db:Session):
    try:
        code = code.upper()
        db_subject = db.query(Subject).filter(Subject.code == code).first()
        if not db_subject:
            raise HTTPException(status_code=404,detail='subject not found')
        
        db.delete(db_subject)
        db.commit()

        return {
            "message": "Subject deleted successfully"
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        return {
            "error":f"{str(e)}"
        }
