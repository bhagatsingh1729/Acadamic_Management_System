from app.services.class_session_services.class_session_services import (
    create_class_session_service,
    get_all_class_session_service,
    get_class_session_of_faculty_service,
    delete_class_session_service,
)
from app.core.dependencies import get_db, require_roles
from fastapi import APIRouter, Depends, HTTPException      
from sqlalchemy.orm import Session
from app.schemas.services_schemas.class_session_schemas.class_session_schemas import (
    ClassSessionCreateRequest,  
)
from app.models.models import Faculty, Subject, User
from typing import List, Dict, Any, Optional
router = APIRouter(prefix="/class-sessions", tags=["Class Sessions"])

@router.post("", summary="Create a class session [admin | super_admin]")
def create_class_session(
    data: ClassSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):

    return create_class_session_service(db=db, data=data)

@router.get("", summary="Get all class sessions [admin | super_admin]")
def get_all_class_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return get_all_class_session_service(db=db)

@router.get("/faculty/{employee_id}", summary="Get class sessions for a specific faculty member [admin | super_admin]")
def get_class_sessions_for_faculty(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin",'super_admin','faculty'))
):
    employee_id = employee_id.upper()
    if current_user.role == 'faculty':
        # If the user is a faculty, ensure they can only access their own sessions
        faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        if not faculty or faculty.employee_id != employee_id:
            raise HTTPException(status_code=403, detail="Access forbidden: You can only access your own class sessions.")   
    return get_class_session_of_faculty_service(db=db, employee_id=employee_id)

@router.delete("/delete/{class_session_id}", summary="Delete a class session [admin | super_admin]")
def delete_class_session_route(
    class_session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin"))
):
    return delete_class_session_service(db=db, class_session_id=class_session_id)