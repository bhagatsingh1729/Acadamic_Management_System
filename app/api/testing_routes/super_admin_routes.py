from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.super_admin_schema import (
    SuperAdminCreate,
    SuperAdminUpdate,
    SuperAdminResponse
)

from app.crud.fundamental_crud.super_admin_crud import (
    create_super_admin,
    get_super_admin,
    update_super_admin,
    delete_super_admin,
    get_super_admin_data
)


router = APIRouter(
    prefix="/super-admin",
    tags=["Super Admin"]
)


# =========================================================
# CREATE
# =========================================================

@router.post(
    "/",
    response_model=SuperAdminResponse
)
def create_super_admin_route(
    data: SuperAdminCreate,
    db: Session = Depends(get_db)
):

    return create_super_admin(
        db=db,
        data=data
    )


# =========================================================
# GET
# =========================================================

@router.get(
    "/",
    response_model=SuperAdminResponse
)
def get_super_admin_route(
    db: Session = Depends(get_db)
):

    return get_super_admin(db)


# =========================================================
# UPDATE
# =========================================================

@router.put(
    "/",
    response_model=SuperAdminResponse
)
def update_super_admin_route(
    data: SuperAdminUpdate,
    db: Session = Depends(get_db)
):

    return update_super_admin(
        db=db,
        data=data
    )


# =========================================================
# DELETE
# =========================================================

@router.delete("/")
def delete_super_admin_route(
    db: Session = Depends(get_db)
):

    return delete_super_admin(db)


# =========================================================
# GET USER DATA
# =========================================================

@router.get("/user")
def get_super_admin_user_data_route(
    db: Session = Depends(get_db)
):

    return get_super_admin_data(db)