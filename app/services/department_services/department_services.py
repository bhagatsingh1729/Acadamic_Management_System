from app.schemas.services_schemas.super_admin_schemas.department_schemas import (
    DepartmentCreate,
    DepartmentUpdate
)

from app.models.models import Department

from app.crud.fundamental_crud.department_crud import (
    create_department,
    update_department,
    delete_department,
    get_all_departments,
    get_department_by_id
)
from fastapi import HTTPException
from sqlalchemy.orm import Session

# Create
def create_department_service(data:DepartmentCreate,db:Session):
    return create_department(department_data=data,db=db)

# Read
def get_all_departments_service(db:Session):
    return get_all_departments(db)

def get_department_via_uid(dept_uid:str,db:Session):
    dept_uid = dept_uid.upper()
    dept_db = db.query(Department).filter(Department.dept_uid == dept_uid).first()
    
    if not dept_db:
        raise HTTPException(status_code=404,detail='Department not found')
    return dept_db

# Update
def update_department_service(dept_uid:str,data:DepartmentUpdate,db:Session):
    dept_uid = dept_uid.upper()
    dept_db = db.query(Department).filter(Department.dept_uid == dept_uid).first()
    
    if not dept_db:
        raise HTTPException(status_code=404,detail='Department not found')
    
    return update_department(db=db,department_id=dept_db.id,department_data=data)

# Delete
def delete_department_service(dept_uid:str,db:Session):
    dept_uid = dept_uid.upper()
    dept_db = db.query(Department).filter(Department.dept_uid == dept_uid).first()
    
    if not dept_db:
        raise HTTPException(status_code=404,detail='Department not found')
    
    return delete_department(department_id=dept_db.id,db=db)