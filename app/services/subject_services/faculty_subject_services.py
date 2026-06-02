from app.crud.fundamental_crud.faculty_subject_crud import (
    assign_subject_to_faculty,
)
from app.schemas.fundamental_schemas.faculty_subject_schema import (
    FacultySubjectCreate,
)
from app.schemas.services_schemas.subject_schemas.faculty_subject_schemas import (
    FacultySubjectRequest,
    FacultySchema,
    SubjectSchema,
    FacultySubjectResponse,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import Subject,Faculty,FacultySubject
from typing import Optional

def assign_subject_to_faculty_service(db:Session,data:FacultySubjectRequest):
    data.employee_id = data.employee_id.upper()
    data.code = data.code.upper()

    db_faculty = db.query(Faculty).filter(Faculty.employee_id == data.employee_id).first()
    db_subject = db.query(Subject).filter(Subject.code == data.code).first()

    if not db_faculty or not db_subject:
        raise HTTPException(status_code=400,detail='either faculty or subject does not exist')
    
    try:
        data_payload = FacultySubjectCreate(
            faculty_id = db_faculty.id,
            subject_id = db_subject.id
        )
        mapping = assign_subject_to_faculty(db=db,data=data_payload)
        db.commit()
        db.refresh(mapping)

        return FacultySubjectResponse(
            employee_id=FacultySchema.model_validate(db_faculty),
            code=SubjectSchema.model_validate(db_subject)
        )
    except HTTPException:
        db.rollback()
        raise

def get_subjects_of_faculty_service(employee_id:str,db:Session):
    employee_id = employee_id.upper()

    db_faculty = db.query(Faculty).filter(Faculty.employee_id == employee_id).first()

    if not db_faculty:
        raise HTTPException(status_code=404,detail='faculty not found')
    
    return db_faculty.subjects

def get_faculties_of_subject_service(subject_code:str,db:Session):
    subject_code = subject_code.upper()

    db_subject = db.query(Subject).filter(Subject.code == subject_code).first()
    if not db_subject:
        raise HTTPException(status_code=404,detail='subject not found')
    
    try:
        return db_subject.faculty_members
    except HTTPException:
        raise

def delete_faculty_subject_service(employee_id:str,subject_code:str,db:Session):
    employee_id = employee_id.upper()
    subject_code = subject_code.upper()

    db_faculty = db.query(Faculty).filter(Faculty.employee_id == employee_id).first()
    db_subject = db.query(Subject).filter(Subject.code == subject_code).first()

    if not db_faculty or not db_subject:
        raise HTTPException(status_code=400,detail='either faculty or subject does not exist')
    
    mapping = db.query(FacultySubject).filter(
        FacultySubject.faculty_id == db_faculty.id,
        FacultySubject.subject_id == db_subject.id
    ).first()

    if not mapping:
        raise HTTPException(status_code=404,detail='mapping does not exist')
    
    try:
        db.delete(mapping)
        db.commit()
        return {"message":"delete success"}
    except HTTPException:
        db.rollback()
        raise
        

