from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.models import User, Faculty, Department
from app.schemas.fundamental_schemas.faculty_schema import FacultyCreate, FacultyUpdate
from app.core.security import hash_password



# =========================
# CREATE FACULTY
# =========================
def create_faculty(db: Session, faculty_data: FacultyCreate):

    # -------------------------
    # check email already exists
    # -------------------------
    existing_email = (
        db.query(User)
        .filter(User.email == faculty_data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="email already exists"
        )

    # -------------------------
    # check employee_id exists
    # -------------------------
    existing_employee = (
        db.query(Faculty)
        .filter(Faculty.employee_id == faculty_data.employee_id.upper())
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="employee_id already exists"
        )

    # -------------------------
    # validate department
    # -------------------------
    if faculty_data.dept_id is not None:

        department = (
            db.query(Department)
            .filter(Department.id == faculty_data.dept_id)
            .first()
        )

        if not department:
            raise HTTPException(
                status_code=404,
                detail="department not found"
            )

    # -------------------------
    # hash password
    # -------------------------
    hashed_password = hash_password(
        faculty_data.password
    )

    # -------------------------
    # create user
    # -------------------------
    new_user = User(
        name=faculty_data.name,
        email=faculty_data.email,
        password=hashed_password,
        role="faculty",

        phone_no=faculty_data.phone_no,
        dob=faculty_data.dob,
        address=faculty_data.address
    )

    db.add(new_user)
    db.flush()

    # -------------------------
    # create faculty row
    # -------------------------
    new_faculty = Faculty(
        user_id=new_user.id,
        employee_id=faculty_data.employee_id.upper(),
        dept_id=faculty_data.dept_id
    )

    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)

    return new_faculty


# =========================
# GET ALL FACULTY
# =========================
def get_all_faculty(db: Session):

    faculty_list = db.query(Faculty).all()

    return faculty_list


# =========================
# GET FACULTY BY ID
# =========================
def get_faculty_by_id(db: Session, faculty_id: int):

    faculty = (
        db.query(Faculty)
        .filter(Faculty.id == faculty_id)
        .first()
    )

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="faculty not found"
        )

    return faculty


# =========================
# UPDATE FACULTY
# =========================
def update_faculty(
    db: Session,
    faculty_id: int,
    faculty_data: FacultyUpdate
):

    faculty = (
        db.query(Faculty)
        .filter(Faculty.id == faculty_id)
        .first()
    )

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="faculty not found"
        )

    # -------------------------
    # validate department
    # -------------------------
    if faculty_data.dept_id is not None:

        department = (
            db.query(Department)
            .filter(Department.id == faculty_data.dept_id)
            .first()
        )

        if not department:
            raise HTTPException(
                status_code=404,
                detail="department not found"
            )

        faculty.dept_id = faculty_data.dept_id

    # -------------------------
    # update user info
    # -------------------------
    user = faculty.user

    if faculty_data.name is not None:
        user.name = faculty_data.name

    if faculty_data.phone_no is not None:
        user.phone_no = faculty_data.phone_no

    if faculty_data.dob is not None:
        user.dob = faculty_data.dob

    if faculty_data.address is not None:
        user.address = faculty_data.address

    db.commit()
    db.refresh(faculty)

    return faculty


# =========================
# DELETE FACULTY
# =========================
def delete_faculty(db: Session, faculty_id: int):

    faculty = (
        db.query(Faculty)
        .filter(Faculty.id == faculty_id)
        .first()
    )

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="faculty not found"
        )

    # ---------------------------------
    # deleting faculty deletes user too
    # because of ON DELETE CASCADE
    # ---------------------------------
    db.delete(faculty)
    db.delete(faculty.user)#adding this line so that when a faculty is deleted, their associated user record is also deleted
    
    db.commit()

    return {
        "message": "faculty deleted successfully"
    }