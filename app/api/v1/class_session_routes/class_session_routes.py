from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_roles
from app.models.models import Admin, Faculty
from app.schemas.services_schemas.class_session_schemas.class_session_schemas import (
    ClassSessionCreateRequest,  
    ClassSessionResponse,
)
from app.services.class_session_services.class_session_services import (
    create_class_session_service,
    get_all_class_session_service,
    get_class_session_of_faculty_service,
    get_student_classes_service,
    delete_class_session_service,
)

router = APIRouter(prefix="/class-sessions", tags=["Class Sessions"])

# =============================================================
# CREATE SESSION
# =============================================================
@router.post("", summary="Create a class session", status_code=status.HTTP_201_CREATED)
def create_class_session(
    data: ClassSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "super_admin"))
):
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: 
            raise HTTPException(status_code=404, detail="Admin configuration profile missing.")
        enforce_branch_id = admin.branch_id
    
    return create_class_session_service(db=db, data=data, enforce_branch_id=enforce_branch_id)


# =============================================================
# STUDENT PROFILE ENDPOINT (Self)
# =============================================================
@router.get("/students/me", response_model=List[ClassSessionResponse], summary="Get my academic class timetable")
def get_my_classes(
    timeframe: Optional[Literal["today", "recent", "upcoming"]] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("student"))
):
    return get_student_classes_service(db=db, user_id=current_user.id, timeframe=timeframe)


# =============================================================
# UNIFIED ADMIN SEARCH / LISTING
# =============================================================
@router.get("", response_model=List[ClassSessionResponse], summary="Get global class session records")
def get_all_class_sessions(
    timeframe: Optional[Literal["today", "recent", "upcoming"]] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "super_admin"))
):
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: 
            raise HTTPException(status_code=404, detail="Admin profile context missing.")
        enforce_branch_id = admin.branch_id
    
    return get_all_class_session_service(db=db, enforced_branch_id=enforce_branch_id, timeframe=timeframe)


# =============================================================
# FACULTY PROFILE ENDPOINT (Self)
# =============================================================
@router.get("/faculty/me", response_model=List[ClassSessionResponse], summary="Get current logged-in faculty sessions")
def get_faculty_classes(
    timeframe: Optional[Literal["today", "recent", "upcoming"]] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles('faculty'))
):
    faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty employment anchor missing.")
        
    return get_class_session_of_faculty_service(db=db, employee_id=faculty.employee_id, timeframe=timeframe)


# =============================================================
# ADMINISTRATIVE FACULTY TARGETED SEARCH
# =============================================================
@router.get("/faculty/{employee_id}", response_model=List[ClassSessionResponse], summary="Get sessions scoped to a target faculty ID")
def get_class_sessions_for_faculty(
    employee_id: str,
    timeframe: Optional[Literal["today", "recent", "upcoming"]] = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "super_admin", "faculty"))
):
    if current_user.role == 'faculty':
        faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
        if not faculty or faculty.employee_id != employee_id.upper():
            raise HTTPException(status_code=403, detail="Access Forbidden: Cannot read alternate instructor schedules.") 
            
    return get_class_session_of_faculty_service(db=db, employee_id=employee_id, timeframe=timeframe)


# =============================================================
# DELETE ACTION ROUTE
# =============================================================
@router.delete("/delete/{class_session_id}", summary="Remove a scheduled class session slot")
def delete_class_session_route(
    class_session_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("admin", "super_admin"))
):
    enforce_branch_id = None
    if current_user.role == 'admin':
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin: 
            raise HTTPException(status_code=404, detail="Admin profile context missing.")
        enforce_branch_id = admin.branch_id
    
    return delete_class_session_service(db=db, class_session_id=class_session_id, enforce_branch_id=enforce_branch_id)