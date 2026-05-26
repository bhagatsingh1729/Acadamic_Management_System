# =========================================================
# hod_crud.py
# =========================================================

from sqlalchemy.orm import Session



from app.models.models import User, Department, HOD
from app.schemas.fundamental_schemas.hod_schema import HodCreate
from app.core.security import hash_password



def create_hod(
    db: Session,
    data: HodCreate
):

    # ---------------------------------------------------
    # existing email
    # ---------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_user:
        raise ValueError(
            "email already exists"
        )

    # ---------------------------------------------------
    # department validation
    # ---------------------------------------------------

    department = (
        db.query(Department)
        .filter(Department.id == data.department_id)
        .first()
    )

    if not department:
        raise ValueError(
            "department not found"
        )

    # ---------------------------------------------------
    # one hod per department
    # ---------------------------------------------------

    existing_hod = (
        db.query(HOD)
        .filter(HOD.department_id == data.department_id)
        .first()
    )

    if existing_hod:
        raise ValueError(
            "department already has a hod"
        )

    # ---------------------------------------------------
    # employee_id unique
    # ---------------------------------------------------
    """"
    existing_employee_id = (
        db.query(HOD)
        .filter(HOD.employee_id == data.employee_id)
        .first()
    )

    if existing_employee_id:
        raise ValueError(
            "employee_id already exists"
        )
    """
    # ---------------------------------------------------
    # create user
    # ---------------------------------------------------

    hashed_password = hash_password(
        data.password
    )

    user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        role="hod"
    )

    db.add(user)

    db.flush()

    # ---------------------------------------------------
    # create hod
    # ---------------------------------------------------

    hod = HOD(
        user_id=user.id,
        department_id=data.department_id,
        #employee_id=data.employee_id
    )

    db.add(hod)

    db.commit()

    db.refresh(hod)

    return hod


def get_all_hods(
    db: Session
):

    hods = (
        db.query(HOD)
        .all()
    )

    return hods


def get_hod_by_id(
    db: Session,
    hod_id: int
):

    hod = (
        db.query(HOD)
        .filter(HOD.id == hod_id)
        .first()
    )

    if not hod:
        raise ValueError(
            "hod not found"
        )

    return hod


def delete_hod(
    db: Session,
    hod_id: int
):

    hod = (
        db.query(HOD)
        .filter(HOD.id == hod_id)
        .first()
    )

    if not hod:
        raise ValueError(
            "hod not found"
        )

    db.delete(hod)
    db.delete(hod.user)#adding this line so that when a hod is deleted, their associated user record is also deleted

    db.commit()

    return {
        "message": "hod deleted successfully"
    }