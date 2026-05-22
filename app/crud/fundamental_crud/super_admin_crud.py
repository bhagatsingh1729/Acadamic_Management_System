from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import User, SuperAdmin

from app.schemas.fundamental_schemas.super_admin_schema import (
    SuperAdminCreate,
    SuperAdminUpdate
)

from app.utils.security import hash_password
from sqlalchemy.exc import IntegrityError

# =========================================================
# CREATE SUPER ADMIN
# =========================================================




def create_super_admin(
    db: Session,
    data: SuperAdminCreate
):

    existing_super_admin = db.query(SuperAdmin).first()

    if existing_super_admin:
        raise HTTPException(
            status_code=400,
            detail="super admin already exists"
        )

    existing_email = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="email already exists"
        )

    hashed_password = hash_password(data.password)

    new_user = User(
        name=data.name,
        email=data.email,
        password=hashed_password,
        role="super_admin",
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )

    db.add(new_user)

    db.flush()

    new_super_admin = SuperAdmin(
        user_id=new_user.id
    )

    db.add(new_super_admin)

    try:
        db.commit()

    except IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="database integrity error"
        )

    db.refresh(new_super_admin)

    return new_super_admin


# =========================================================
# GET SUPER ADMIN
# =========================================================

def get_super_admin(db: Session):

    super_admin = (
        db.query(SuperAdmin)
        .first()
    )

    if not super_admin:
        raise HTTPException(
            status_code=404,
            detail="super admin not found"
        )

    return super_admin


# =========================================================
# UPDATE SUPER ADMIN
# =========================================================

def update_super_admin(
    db: Session,
    data: SuperAdminUpdate
):

    super_admin = (
        db.query(SuperAdmin)
        .first()
    )

    if not super_admin:
        raise HTTPException(
            status_code=404,
            detail="super admin not found"
        )

    user = super_admin.user

    # -------------------------------------------------
    # NAME
    # -------------------------------------------------

    if data.name is not None:
        user.name = data.name

    # -------------------------------------------------
    # EMAIL
    # -------------------------------------------------

    if data.email is not None:

        existing_email = (
            db.query(User)
            .filter(
                User.email == data.email,
                User.id != user.id
            )
            .first()
        )

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="email already exists"
            )

        user.email = data.email

    # -------------------------------------------------
    # PASSWORD
    # -------------------------------------------------

    if data.password is not None:
        user.password = hash_password(data.password)

    # -------------------------------------------------
    # PHONE
    # -------------------------------------------------

    if data.phone_no is not None:
        user.phone_no = data.phone_no

    # -------------------------------------------------
    # DOB
    # -------------------------------------------------

    if data.dob is not None:
        user.dob = data.dob

    # -------------------------------------------------
    # ADDRESS
    # -------------------------------------------------

    if data.address is not None:
        user.address = data.address

    db.commit()

    db.refresh(super_admin)

    return super_admin


# =========================================================
# DELETE SUPER ADMIN
# =========================================================

def delete_super_admin(db: Session):

    super_admin = (
        db.query(SuperAdmin)
        .first()
    )

    if not super_admin:
        raise HTTPException(
            status_code=404,
            detail="super admin not found"
        )

    user = super_admin.user

    db.delete(super_admin)

    db.delete(user)

    db.commit()

    return {
        "detail": "super admin deleted successfully"
    }


# =========================================================
# GET USER DATA
# =========================================================

def get_super_admin_data(db: Session):

    super_admin = (
        db.query(SuperAdmin)
        .first()
    )

    if not super_admin:
        raise HTTPException(
            status_code=404,
            detail="super admin not found"
        )

    return super_admin.user