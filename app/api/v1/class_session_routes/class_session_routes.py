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
from app.models.models import Faculty, Subject, User,Admin
from typing import List, Dict, Any, Optional
router = APIRouter(prefix="/class-sessions", tags=["Class Sessions"])

@router.post("", summary="Create a class session")
def create_class_session(
    data: ClassSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: raise HTTPException(status_code=404, detail="Admin not found")
        enforce_branch_id = admin.branch_id
    
    return create_class_session_service(db=db, data=data, enforce_branch_id=enforce_branch_id)

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

@router.get("/faculty/{employee_id}", summary="Get sessions for a specific faculty")
def get_class_sessions_for_faculty(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty"))
):
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
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: raise HTTPException(status_code=404, detail="Admin not found")
        enforce_branch_id = admin.branch_id
    
    return delete_class_session_service(db=db, class_session_id=class_session_id, enforce_branch_id=enforce_branch_id)