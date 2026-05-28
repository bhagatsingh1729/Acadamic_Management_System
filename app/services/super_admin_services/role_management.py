#===========General imports============================
from pydantic import EmailStr
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional
#===================================================
# Service level Schemas import
#===================================================
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminCreate,
    AdminUpdate,
    AdminResponse,
    StudentCreateRequest,
    StudentUpdateRequest
)
from app.schemas.services_schemas.student_schemas.student_schema import (
    StudentCreateRequest,
    StudentUpdateRequest
)
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminResponse
)
#=============================================
# Fundamental Crud import
#=============================================
from app.crud.fundamental_crud.admin_crud import (
    create_admin
)
from app.crud.fundamental_crud.admin_crud import (
    create_admin,
    update_admin
)
from app.crud.fundamental_crud.student_crud import (
    create_student,
    get_all_students,
    get_student_by_id,
    get_student_by_usn,
    get_students_by_cohort,
    get_students_by_branch,
    update_student,
    delete_student
)
#=====================================================
# Fundamental schema imports
#=====================================================
from app.schemas.fundamental_schemas.student_schema import (
    StudentCreate,
    StudentUpdate
)
from app.schemas.fundamental_schemas import admin_schema
from app.schemas.fundamental_schemas import admin_schema
#==========================================================
from app.core.security import hash_password
#==========================================================
# Models import
#==========================================================
from app.models.models import Branch,Admin,User,Student

#==========================================================





def create_admin_service(data:AdminCreate,db:Session):

    branch_uid = data.branch_uid.upper()
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404,detail='branch not found')
    data_payload = admin_schema.AdminCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        branch_id=branch_db.id,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )
    return create_admin(db=db,admin_data=data_payload)

def get_all_admin_service(db:Session):
    admins = db.query(Admin).all()
    if not admins:
        raise HTTPException(status_code=400,detail='no admin found')
    return admins

def update_admin_service(data:AdminUpdate,email:EmailStr,db:Session):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404,detail='user not found')
    
    if db_user.role != 'admin':
        raise HTTPException(status_code=400,detail='the user is not admin')
    
    db_admin = db.query(Admin).filter(Admin.user_id == db_user.id).first()
    if not db_admin:
        raise HTTPException(status_code=404,detail='admin does not exist in admin table')
    
    if data.branch_uid:
        branch_data = db.query(Branch).filter(Branch.branch_uid == data.branch_uid.upper()).first()
        if not branch_data:
            raise HTTPException(status_code=400,detail='branch does not exist')
        
    admin_data = admin_schema.AdminUpdate(
        name=data.name,
        phone_no=data.phone_no,
        dob=data.phone_no,
        address=data.address,
        branch_id=branch_data.id
    )
    return update_admin(db,db_admin.id,admin_data=admin_data)



# Get user by email
def get_user_via_email_service(email:EmailStr,db:Session):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404,detail='user not found')
    return db_user

# get all user
def get_all_user_service(db:Session):
    db_users = db.query(User).limit(30)
    if not db_users:
        raise HTTPException(status_code=404,detail='users not found')
    return db_users

def get_user_via_role(role:str,db:Session):
    
    if role not in ['admin','student','hod','faculty','super_admin']:
        raise HTTPException(status_code=400,detail='bad request')
    
    db_users = db.query(User).filter(User.role == role).limit(30)

    if not db_users:
        raise HTTPException(status_code=404,detail='not found')
    return db_users

#--------------------------------
# Student role management
#--------------------------------
def create_student_service(data:StudentCreateRequest,db:Session):
    
    branch_uid = data.branch_uid.upper()
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404,detail='branch not found')
    

    data_payload = StudentCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        usn = data.usn,
        semester=data.semester,
        batch=data.batch,
        section=data.section,
        branch_id= branch_db.id,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )

    return create_student(db=db,data=data_payload)


# =============================================================
# GET ALL STUDENTS
# =============================================================
def get_all_students_service(
    db: Session
):
    return get_all_students(db)


# =============================================================
# GET STUDENT BY USN
# =============================================================
def get_student_by_usn_service(
    db: Session,
    usn: str,
):
    student = get_student_by_usn(db, usn)
    return student





# =============================================================
# UPDATE STUDENT
# =============================================================
def update_student_service(
    db: Session,
    usn: str,
    data: StudentUpdateRequest
):
    # First check student exists and get their record
    student = get_student_by_usn(db,usn)
    if not student:
        raise HTTPException(status_code=404,detail='student not found')
    # ↑ raises HTTPException(404) if not found

    if data.branch_uid:
        branch_uid = data.branch_uid.upper()
        branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    
        if not branch_db:
            raise HTTPException(status_code=400,detail='branch does not exist')
    
    # Build the CRUD-level update schema
    update_data = StudentUpdate(
        semester=data.semester,
        batch=data.batch,
        branch_id=branch_db.id,
        section=data.section,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )

    return update_student(db, student.id, update_data)


# =============================================================
# DELETE STUDENT
# =============================================================
def delete_student_service(
    db: Session,
    usn: str
):
    student = get_student_by_usn(db,usn)

    if not student:
        raise HTTPException(status_code=404,detail='student not found')

    return delete_student(db, student.id)