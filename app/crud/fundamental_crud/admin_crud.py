from sqlalchemy.orm import Session
from fastapi import HTTPException
from passlib.context import CryptContext
from app.utils.security import hash_password
from app.models.models import User, Admin, Branch

from app.schemas.fundamental_schemas.admin_schema import (
    AdminCreate,
    AdminUpdate
)





# =========================
# CREATE ADMIN
# =========================
def create_admin(
    db: Session,
    admin_data: AdminCreate
):

    # -------------------------
    # email exists
    # -------------------------
    existing_email = (
        db.query(User)
        .filter(User.email == admin_data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="email already exists"
        )

    # -------------------------
    # validate branch
    # -------------------------
    if admin_data.branch_id is not None:

        branch = (
            db.query(Branch)
            .filter(Branch.id == admin_data.branch_id)
            .first()
        )

        if not branch:
            raise HTTPException(
                status_code=404,
                detail="branch not found"
            )

        # -------------------------
        # one admin per branch
        # -------------------------
        existing_branch_admin = (
            db.query(Admin)
            .filter(Admin.branch_id == admin_data.branch_id)
            .first()
        )

        if existing_branch_admin:
            raise HTTPException(
                status_code=400,
                detail="branch already has an admin"
            )

    # -------------------------
    # hash password
    # -------------------------
    hashed_password = hash_password(admin_data.password)

    # -------------------------
    # create user
    # -------------------------
    new_user = User(
        name=admin_data.name,
        email=admin_data.email,
        password=hashed_password,
        role="admin",

        phone_no=admin_data.phone_no,
        dob=admin_data.dob,
        address=admin_data.address
    )

    db.add(new_user)
    db.flush()

    # -------------------------
    # create admin
    # -------------------------
    new_admin = Admin(
        user_id=new_user.id,
        branch_id=admin_data.branch_id
    )

    db.add(new_admin)

    db.commit()
    db.refresh(new_admin)

    return new_admin


# =========================
# GET ALL ADMINS
# =========================
def get_all_admins(db: Session):

    admins = db.query(Admin).all()

    return admins


# =========================
# GET ADMIN BY ID
# =========================
def get_admin_by_id(
    db: Session,
    admin_id: int
):

    admin = (
        db.query(Admin)
        .filter(Admin.id == admin_id)
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="admin not found"
        )

    return admin


# =========================
# UPDATE ADMIN
# =========================
def update_admin(
    db: Session,
    admin_id: int,
    admin_data: AdminUpdate
):

    admin = (
        db.query(Admin)
        .filter(Admin.id == admin_id)
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="admin not found"
        )

    # -------------------------
    # update branch
    # -------------------------
    if admin_data.branch_id is not None:

        branch = (
            db.query(Branch)
            .filter(Branch.id == admin_data.branch_id)
            .first()
        )

        if not branch:
            raise HTTPException(
                status_code=404,
                detail="branch not found"
            )

        existing_branch_admin = (
            db.query(Admin)
            .filter(
                Admin.branch_id == admin_data.branch_id,
                Admin.id != admin.id
            )
            .first()
        )

        if existing_branch_admin:
            raise HTTPException(
                status_code=400,
                detail="branch already has another admin"
            )

        admin.branch_id = admin_data.branch_id

    # -------------------------
    # update user info
    # -------------------------
    user = admin.user

    if admin_data.name is not None:
        user.name = admin_data.name

    if admin_data.phone_no is not None:
        user.phone_no = admin_data.phone_no

    if admin_data.dob is not None:
        user.dob = admin_data.dob

    if admin_data.address is not None:
        user.address = admin_data.address

    db.commit()
    db.refresh(admin)

    return admin


# =========================
# DELETE ADMIN
# =========================
def delete_admin(
    db: Session,
    admin_id: int
):

    admin = (
        db.query(Admin)
        .filter(Admin.id == admin_id)
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=404,
            detail="admin not found"
        )

    # --------------------------------
    # deleting admin deletes user too
    # because of ON DELETE CASCADE
    # --------------------------------
    db.delete(admin)

    db.commit()

    return {
        "message": "admin deleted successfully"
    }