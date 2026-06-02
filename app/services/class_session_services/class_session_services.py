from app.schemas.fundamental_schemas.class_session_schema import (
    ClassSessionCreate,
)
from app.schemas.services_schemas.class_session_schemas.class_session_schemas import (
    ClassSessionCreateRequest,
    ClassSessionResponse,
)
from app.crud.fundamental_crud.class_session_crud import (
    create_class_session,
    delete_class_session,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import ClassSession,Faculty,Subject, User
from typing import Optional 

def create_class_session_service(db:Session,data:ClassSessionCreateRequest):
    data.employee_id = data.employee_id.upper()
    data.code = data.code.upper()

    db_faculty = db.query(Faculty).filter(Faculty.employee_id == data.employee_id).first()
    db_subject = db.query(Subject).filter(Subject.code == data.code).first()

    if not db_faculty or not db_subject:
        raise HTTPException(status_code=400,detail='faculty or subject does not exist')
    
    try:
        data_payload = ClassSessionCreate(
            faculty_id=db_faculty.id,
            subject_id=db_subject.id,
            semester=data.semester,
            date=data.date,
            start_time=data.start_time,
            end_time=data.end_time,
            batch=data.batch,
            section=data.section
        )
        class_session = create_class_session(db=db,session_data=data_payload)
        db.commit()
        db.refresh(class_session)
        return {'message':'successfully create class Session'}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        return {'message':str(e)}

def get_all_class_session_service(db:Session):
    
    db_class_session = (
        db.query(ClassSession)
        .join(Faculty, ClassSession.faculty_id == Faculty.id)
        .join(User, Faculty.user_id == User.id)
        .join(Subject, ClassSession.subject_id == Subject.id)
        .with_entities(
            ClassSession.id.label("session_id"),
            User.name.label("faculty_name"),
            Faculty.employee_id.label("employee_id"),
            Subject.code.label("code"),
            ClassSession.semester,
            ClassSession.date,
            ClassSession.start_time,
            ClassSession.end_time,
            ClassSession.batch,
            ClassSession.section
        ) 
    ).all()

    return [
        ClassSessionResponse(
            session_id=session.session_id,
            faculty_name=session.faculty_name,
            employee_id=session.employee_id,
            code=session.code,
            semester=session.semester,
            date=session.date,
            start_time=session.start_time,
            end_time=session.end_time,
            batch=session.batch,
            section=session.section
        )
        for session in db_class_session
    ]

def get_class_session_of_faculty_service(db:Session,employee_id:str,semester:Optional[int]=None):
    eomployee_id = employee_id.upper()
    query = (
        db.query(ClassSession)
        .join(Faculty, ClassSession.faculty_id == Faculty.id)
        .join(User, Faculty.user_id == User.id)
        .join(Subject, ClassSession.subject_id == Subject.id)
        .filter(Faculty.employee_id == employee_id)
        .with_entities(
            ClassSession.id.label("session_id"),
            User.name.label("faculty_name"),
            Faculty.employee_id.label("employee_id"),
            Subject.code.label("code"),
            ClassSession.semester,
            ClassSession.date,
            ClassSession.start_time,
            ClassSession.end_time,
            ClassSession.batch,
            ClassSession.section
        )
    ).all()

    if not query:
        raise HTTPException(status_code=404,detail='no class session found for the given employee id')
    
    return [
        ClassSessionResponse(
            session_id=session.session_id,
            faculty_name=session.faculty_name,
            employee_id=session.employee_id,
            code=session.code,
            semester=session.semester,
            date=session.date,
            start_time=session.start_time,
            end_time=session.end_time,
            batch=session.batch,
            section=session.section
        )
        for session in query
    ]

def delete_class_session_service(db:Session,class_session_id:int):
    try:
        db_class_session = db.query(ClassSession).filter(ClassSession.id == class_session_id).first()
        if not db_class_session:
            raise HTTPException(status_code=404,detail='class session not found')   
        db.delete(db_class_session)
        db.commit()
        return {'message':'successfully deleted class session'}
    except ValueError as e:
        raise HTTPException(status_code=404,detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))