from app.services.class_session_services.class_session_services import (
    create_class_session_service,
    get_all_class_session_service,
    get_class_session_of_faculty_service,
    delete_class_session_service,
)
from app.core.dependencies import get_db, require_roles
from fastapi import APIRouter, Depends, HTTPException      
from sqlalchemy.orm import Session,aliased
from app.schemas.services_schemas.class_session_schemas.class_session_schemas import (
    ClassSessionCreateRequest,  
    ClassSessionResponse,
)
from app.models.models import Faculty, Subject, User,Admin,ClassSession,StudentSubject,Student
from typing import List, Dict, Any, Optional
router = APIRouter(prefix="/class-sessions", tags=["Class Sessions"])

@router.post("", summary="Create a class session")
def create_class_session(
    data: ClassSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    """
    the admin can create class session for his/her branch only.
    super admin can create for all the branches.
    """
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: raise HTTPException(status_code=404, detail="Admin not found")
        enforce_branch_id = admin.branch_id
    
    return create_class_session_service(db=db, data=data, enforce_branch_id=enforce_branch_id)

@router.get("/students/me", response_model=list[ClassSessionResponse])
def get_my_classes(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("student"))
):
    # The role check is redundant if require_roles already handles it,
    # but kept here for parity with your snippet.
    
    db_classes = (
        db.query(ClassSession)
        .join(StudentSubject, ClassSession.subject_id == StudentSubject.subject_id)
        .join(Faculty, Faculty.id == ClassSession.faculty_id)
        .join(Student, StudentSubject.student_id == Student.id)
        .join(Subject, Subject.id == ClassSession.subject_id)
        .join(User, Faculty.user_id == User.id)
        .filter(
            Student.id == current_user.student.id,
            ClassSession.semester == current_user.student.semester,
            ClassSession.batch == current_user.student.batch,
            ClassSession.section == current_user.student.section
        ).with_entities(
            ClassSession.id.label("session_id"),
            User.name.label("faculty_name"),
            Faculty.employee_id.label("employee_id"), # Corrected label
            Subject.code.label("code"),               # Added label for safety
            ClassSession.semester,
            ClassSession.date,
            ClassSession.start_time,
            ClassSession.end_time,
            ClassSession.batch,
            ClassSession.section
        )
        .all() # Make sure to execute the query
    )

    if not db_classes:
        raise HTTPException(status_code=404, detail="No classes found for you")

    return db_classes

@router.get("", summary="Get all class sessions")
def get_all_class_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: raise HTTPException(status_code=404, detail="Admin not found")
        enforce_branch_id = admin.branch_id
    
    return get_all_class_session_service(db=db, enforced_branch_id=enforce_branch_id)

@router.get("/faculty/me", response_model=list[ClassSessionResponse])
def get_faculty_classes(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('faculty'))
):
    """
    this endpoint return all classes of faculty(current_user)
    """
    if current_user.role == 'faculty':
        db_classes = (
            db.query(
                ClassSession.id.label("session_id"),
                User.name.label("faculty_name"),
                Faculty.employee_id,
                Subject.code.label("code"),
                ClassSession.semester,
                ClassSession.date,
                ClassSession.start_time,
                ClassSession.end_time,
                ClassSession.batch,
                ClassSession.section,
            )
            .join(Faculty, ClassSession.faculty_id == Faculty.id)
            .join(User, Faculty.user_id == User.id)
            .join(Subject, ClassSession.subject_id == Subject.id)
            .filter(ClassSession.faculty_id == current_user.faculty.id)
            .all()
        )

        if not db_classes:
            raise HTTPException(status_code=404, detail="no classes found for you")

        return db_classes



@router.get("/faculty/{employee_id}", summary="Get sessions for a specific faculty")
def get_class_sessions_for_faculty(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty"))
):
    """
    this endpoint is useful for roles like admin and super_admin to see 
    classes of a specific faculty
    """
    employee_id = employee_id.upper()
    if current_user.role == 'faculty':
        faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        if not faculty or faculty.employee_id != employee_id:
            raise HTTPException(status_code=403, detail="Access forbidden") 
            
    return get_class_session_of_faculty_service(db=db, employee_id=employee_id)

@router.delete("/delete/{class_session_id}", summary="Delete a class session")
def delete_class_session_route(
    class_session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    """
    admin can delete class session for his/her branch.
    super admin can delete for all branches.
    """
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: raise HTTPException(status_code=404, detail="Admin not found")
        enforce_branch_id = admin.branch_id
    
    return delete_class_session_service(db=db, class_session_id=class_session_id, enforce_branch_id=enforce_branch_id)