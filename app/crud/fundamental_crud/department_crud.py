from sqlalchemy.orm import Session

from app.models.models import Department,User,HOD,Faculty
from app.schemas.fundamental_schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate
)
from fastapi import HTTPException

# ------------------------------------------------
# CREATE DEPARTMENT
# ------------------------------------------------
def create_department(
    db: Session,
    department_data: DepartmentCreate
):
    department_data_name = department_data.name.upper()
    department_data_uid = department_data.dept_uid.upper()
    # check department name uniqueness
    existing_department = (
        db.query(Department)
        .filter(Department.name == department_data_name)
        .first()
    )

    if existing_department:
        raise HTTPException(status_code=409,detail="Department name already exists")

    # check uid uniqueness
    existing_uid = (
        db.query(Department)
        .filter(Department.dept_uid == department_data_uid)
        .first()
    )

    if existing_uid:
        raise HTTPException(status_code=409,detail="Department UID already exists")

    new_department = Department(
        name=department_data.name.upper(),
        dept_uid=department_data.dept_uid.upper()
    )

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department


# ------------------------------------------------
# GET ALL DEPARTMENTS
# ------------------------------------------------
def get_all_departments(db: Session):

    departments = db.query(Department).all()

    return departments


# ------------------------------------------------
# GET SINGLE DEPARTMENT
# ------------------------------------------------
def get_department_by_id(
    db: Session,
    department_id: int
):

    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(status_code=404,detail='Department not found')

    return department


# ------------------------------------------------
# UPDATE DEPARTMENT
# ------------------------------------------------
def update_department(
    db: Session,
    department_id: int,
    department_data: DepartmentUpdate
):

    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if not department:
        raise HTTPException(status_code=404,detail='department not found')

    
    # update name
    if department_data.name:
        department_data_name = department_data.name.upper()
        existing_name = (
            db.query(Department)
            .filter(
                Department.name == department_data_name,
                Department.id != department_id
            )
            .first()
        )

        if existing_name:
            raise HTTPException(status_code=409,detail="Department name already exists")

        department.name = department_data.name.upper() #making the upper case

    
    # update uid
    if department_data.dept_uid:
        department_data_uid = department_data.dept_uid.upper()
        existing_uid = (
            db.query(Department)
            .filter(
                Department.dept_uid == department_data_uid,
                Department.id != department_id
            )
            .first()
        )

        if existing_uid:
            raise HTTPException(status_code=409,detail="Department UID already exists")

        department.dept_uid = department_data.dept_uid.upper() #making the uid uppercase

    db.commit()
    db.refresh(department)

    return department


# ------------------------------------------------
# DELETE DEPARTMENT
# ------------------------------------------------
def delete_department(db: Session, department_id: int):
    department = db.query(Department).filter(Department.id == department_id).first()
    
    if not department:
        raise HTTPException(status_code=404,detail="Department not found")

    # 1. Handle HOD and their User record
    if department.hod:
        hod_user_id = department.hod.user_id
        db.delete(department.hod) # Delete the HOD record first
        db.query(User).filter(User.id == hod_user_id).delete(synchronize_session=False)

    # 2. Handle Faculty and their User records
    # We collect all faculty IDs to delete their linked users in one bulk query
    faculty_members = department.faculty
    if faculty_members:
        faculty_user_ids = [f.user_id for f in faculty_members]
        
        # Delete Faculty records
        for f in faculty_members:
            db.delete(f)
            
        # Bulk delete all associated Users in one go
        db.query(User).filter(User.id.in_(faculty_user_ids)).delete(synchronize_session=False)

    # 3. Finally, delete the department
    db.delete(department)
    
    db.commit()
    return {"message": "Department and all related users deleted successfully"}