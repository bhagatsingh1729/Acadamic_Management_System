from sqlalchemy.orm import Session

from app.models.models import Department,User,HOD,Faculty
from app.schemas.fundamental_schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate
)


# ------------------------------------------------
# CREATE DEPARTMENT
# ------------------------------------------------
def create_department(
    db: Session,
    department_data: DepartmentCreate
):

    # check department name uniqueness
    existing_department = (
        db.query(Department)
        .filter(Department.name == department_data.name)
        .first()
    )

    if existing_department:
        raise ValueError("Department name already exists")

    # check uid uniqueness
    existing_uid = (
        db.query(Department)
        .filter(Department.dept_uid == department_data.dept_uid)
        .first()
    )

    if existing_uid:
        raise ValueError("Department UID already exists")

    new_department = Department(
        name=department_data.name,
        dept_uid=department_data.dept_uid
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
        raise ValueError("Department not found")

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
        raise ValueError("Department not found")

    # update name
    if department_data.name:

        existing_name = (
            db.query(Department)
            .filter(
                Department.name == department_data.name,
                Department.id != department_id
            )
            .first()
        )

        if existing_name:
            raise ValueError("Department name already exists")

        department.name = department_data.name

    # update uid
    if department_data.dept_uid:

        existing_uid = (
            db.query(Department)
            .filter(
                Department.dept_uid == department_data.dept_uid,
                Department.id != department_id
            )
            .first()
        )

        if existing_uid:
            raise ValueError("Department UID already exists")

        department.dept_uid = department_data.dept_uid

    db.commit()
    db.refresh(department)

    return department


# ------------------------------------------------
# DELETE DEPARTMENT
# ------------------------------------------------
def delete_department(db: Session, department_id: int):
    department = db.query(Department).filter(Department.id == department_id).first()
    
    if not department:
        raise ValueError("Department not found")

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