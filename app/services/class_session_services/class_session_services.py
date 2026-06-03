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
from app.models.models import ClassSession,Faculty,Subject, User,BranchSubject
from typing import Optional 

def create_class_session_service(db:Session,data:ClassSessionCreateRequest,enforce_branch_id:Optional[int] = None):
    data.employee_id = data.employee_id.upper()
    data.code = data.code.upper()

    # For Branch Admin
    if enforce_branch_id is not None:
        db_subject = db.query(Subject).filter(Subject.code == data.code).first()
        if not db_subject:
            raise HTTPException(status_code=404,detail='subject not found')
        subject_branch = db.query(BranchSubject).filter(BranchSubject.subject_id == db_subject.id,BranchSubject.branch_id == enforce_branch_id).first()
        if not subject_branch:
            raise HTTPException(status_code=400,detail='subject does not exist in the specified branch')

    # For Super Admin
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

def get_all_class_session_service(db: Session, enforced_branch_id: Optional[int] = None):
    query = (
        db.query(ClassSession)
        .join(Faculty, ClassSession.faculty_id == Faculty.id)
        .join(User, Faculty.user_id == User.id)
        .join(Subject, ClassSession.subject_id == Subject.id)
    )

    # Only join BranchSubject if we are enforcing a branch
    if enforced_branch_id:
        query = query.join(BranchSubject, Subject.id == BranchSubject.subject_id) \
                     .filter(BranchSubject.branch_id == enforced_branch_id)

    results = query.with_entities(
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
    ).all()

    return [ClassSessionResponse(**session._asdict()) for session in results]

def get_class_session_of_faculty_service(db: Session, employee_id: str):
    employee_id = employee_id.upper()

    """
    This function retrieves class sessions for a specific faculty member based on their employee ID.
    It performs the following steps:
    1. Joins the ClassSession, Faculty, User, and Subject tables to gather
         relevant information about the class sessions.
    2. Filters the results to only include sessions where the Faculty's employee ID matches the provided employee_id.
    3. Selects specific fields to return, including session ID, faculty name, employee
            ID, subject code, semester, date, start time, end time, batch, and section.
    4. If no sessions are found for the given employee ID, it raises a 404 HTTP exception.
    5. Returns a list of ClassSessionResponse objects created from the query results.

    The rule: Always join using the relationship paths between the models. Let the database handle the filtering.
    """
    results = (
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

    if not results:
        raise HTTPException(status_code=404, detail='No class session found for the given employee id')
    
    return [ClassSessionResponse(**session._asdict()) for session in results]

def delete_class_session_service(db:Session,class_session_id:int,enforce_branch_id:Optional[int] = None):
    class_session = db.query(ClassSession).filter(ClassSession.id == class_session_id).first()
    if not class_session:
        raise HTTPException(status_code=404,detail='class session not found')
    
    if enforce_branch_id is not None:
        subject = db.query(Subject).filter(Subject.id == class_session.subject_id).first()
        subject_branch = db.query(BranchSubject).filter(BranchSubject.subject_id == subject.id,BranchSubject.branch_id == enforce_branch_id).first()
        if not subject_branch:
            raise HTTPException(status_code=403,detail='you do not have permission to delete this class session')

    try:
        delete_class_session(db=db,class_session=class_session)
        db.commit()
        return {'message':'successfully deleted class session'}
    except Exception as e:
        db.rollback()
        return {'message':str(e)}
