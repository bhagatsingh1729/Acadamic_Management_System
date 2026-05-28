from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import EmailStr
#====================
# Models
#====================
from app.models.models import Admin
#====================
from app.core.dependencies import require_super_admin

#=========================
# Service level Schema
#=========================
from app.services.super_admin_services.role_management import (
    create_admin_service,
    get_all_admin_service,
    get_user_via_email_service,
    get_all_user_service,
    get_user_via_role,
    update_admin_service,
    #Faculty
    create_faculty_service,
    update_faculty_service,
    delete_faculty_via_emp_id_service,
    get_all_faculty_service,
    get_faculty_via_emp_id_service,
    #student
    create_student_service,
    get_all_students_service,
    update_student_service,
    delete_student_service,
    get_student_by_usn_service,
    #user
    change_user_password_service
)
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminCreate,
    AdminUpdate,
    AdminResponse,
    StudentCreateRequest,
    StudentUpdateRequest,
    StudentResponse,
    FacultyCreateRequest,
    FacultyUpdateRequest,
    FacultyResponse
)
from app.schemas.response_schemas.base_response import UserBasicInfo
#===========================================


router = APIRouter(prefix="/roles", tags=["roles"])

#===============================================
# Admin role management
#===============================================

@router.post("/admins/create",response_model=AdminResponse)
def create_admin_route(data:AdminCreate,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return create_admin_service(data=data,db=db)

@router.get("/admins",response_model=list[AdminResponse])
def get_all_admin_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_admin_service(db)

@router.patch("admins/update/{email}",response_model=AdminResponse)
def update_admin_route(email:EmailStr,data:AdminUpdate,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return update_admin_service(email=email,data=data,db=db)

#==============================================
# User level service
#==============================================
@router.get("/users/{email}",response_model=UserBasicInfo)
def get_user_via_email_route(email:EmailStr,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_user_via_email_service(email,db)

@router.get("/users",response_model=list[UserBasicInfo])
def get_all_users_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_user_service(db)

@router.get("/users/role/{role}",response_model=list[UserBasicInfo])
def get_all_user_via_role(role:str,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_user_via_role(role,db)

@router.patch("/users/update/password/{email}")
def change_user_password_route(email:str,new_password:str,db:Session=Depends(get_db),curren_user=Depends(require_super_admin)):
    return change_user_password_service(email=email,new_password=new_password,db=db)

#======================================
# Faculty role management
#======================================

@router.post("/faculty/create", response_model=FacultyResponse)
def create_faculty_route(
    data: FacultyCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    return create_faculty_service(db=db, data=data)

@router.get("/faculties", response_model=list[FacultyResponse])
def get_all_faculty_route(
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    return get_all_faculty_service(db)

@router.get("/faculty/{emp_id}", response_model=FacultyResponse)
def get_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    return get_faculty_via_emp_id_service(emp_id=emp_id, db=db)

@router.patch("/faculty/update/{emp_id}", response_model=FacultyResponse)
def update_faculty_via_emp_id_route(
    emp_id: str,
    data: FacultyUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    return update_faculty_service(emp_id, data, db)

@router.delete("/faculty/delete/{emp_id}")
def delete_faculty_via_emp_id_route(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_super_admin)
):
    return delete_faculty_via_emp_id_service(emp_id=emp_id, db=db)




#-----------------------------------------
# Student role management
#-----------------------------------------

@router.post("/students/create",response_model=StudentResponse)
def create_student_route(data:StudentCreateRequest,db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return create_student_service(data=data,db=db)

@router.get("/students",response_model=list[StudentResponse])
def get_all_students_route(db:Session=Depends(get_db),current_user=Depends(require_super_admin)):
    return get_all_students_service(db=db)

# =============================================================
# GET /students — List students
# =============================================================
@router.get(
    "",
    response_model=list[StudentResponse],
    summary="List students [super_admin]"
)
def list_students(
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_all_students_service(db)



# =============================================================
# GET /students/{usn} — Get single student by USN
# =============================================================
@router.get(
    "/{usn}",
    response_model=StudentResponse,
    summary="Get student by USN [admin (own branch) | super_admin | faculty | hod]"
)
def get_student(
    usn: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return get_student_by_usn_service(db, usn)


# =============================================================
# PUT /students/{id} — Update student
# =============================================================
@router.put(
    "/update/{usn}",
    response_model=StudentResponse,
    summary="Update student [super_admin]"
)
def update_student(
    usn: str,
    data: StudentUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return update_student_service(db, usn, data)


# =============================================================
# DELETE /students/{id} — Delete student
# =============================================================
@router.delete(
    "/delete/{usn}",
    summary="Delete student [admin (own branch) | super_admin]"
)
def delete_student(
    usn:str,
    db: Session = Depends(get_db),
    current_user=Depends(require_super_admin)
):
    return delete_student_service(db, usn)