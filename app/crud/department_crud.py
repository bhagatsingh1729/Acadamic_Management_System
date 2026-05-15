from sqlalchemy.orm import Session

from app.models.models import Department
from app.schemas.department import (
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
def delete_department(
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

    db.delete(department)
    db.commit()

    return {
        "message": "Department deleted successfully"
    }