from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.admin import (
    AdminCreate,
    AdminUpdate
)

from app.crud.admin_crud import (
    create_admin,
    get_all_admins,
    get_admin_by_id,
    update_admin,
    delete_admin
)


router_admin = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


# =========================
# CREATE ADMIN
# =========================
@router_admin.post("/")
def create_admin_route(
    admin_data: AdminCreate,
    db: Session = Depends(get_db)
):

    return create_admin(db, admin_data)


# =========================
# GET ALL ADMINS
# =========================
@router_admin.get("/")
def get_all_admins_route(
    db: Session = Depends(get_db)
):

    return get_all_admins(db)


# =========================
# GET ADMIN BY ID
# =========================
@router_admin.get("/{admin_id}")
def get_admin_by_id_route(
    admin_id: int,
    db: Session = Depends(get_db)
):

    return get_admin_by_id(
        db,
        admin_id
    )


# =========================
# UPDATE ADMIN
# =========================
@router_admin.put("/{admin_id}")
def update_admin_route(
    admin_id: int,
    admin_data: AdminUpdate,
    db: Session = Depends(get_db)
):

    return update_admin(
        db,
        admin_id,
        admin_data
    )


# =========================
# DELETE ADMIN
# =========================
@router_admin.delete("/{admin_id}")
def delete_admin_route(
    admin_id: int,
    db: Session = Depends(get_db)
):

    return delete_admin(
        db,
        admin_id
    )