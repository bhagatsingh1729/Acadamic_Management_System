from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserLogin,
    UserResponse
)

from app.crud.fundamental_crud.user_crud import (
    create_user,
    get_all_users,
    get_user_by_id,
    get_user_by_email,
    login_user,
    update_user,
    delete_user
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ------------------------------------------------
# CREATE USER
# ------------------------------------------------
@router.post("/", response_model=UserResponse)
def create_user_route(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    try:
        return create_user(
            db,
            user_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ------------------------------------------------
# GET ALL USERS
# ------------------------------------------------
@router.get("/", response_model=list[UserResponse])
def get_all_users_route(
    db: Session = Depends(get_db)
):

    return get_all_users(db)


# ------------------------------------------------
# GET USER BY ID
# ------------------------------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(
    user_id: int,
    db: Session = Depends(get_db)
):

    try:
        return get_user_by_id(
            db,
            user_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ------------------------------------------------
# GET USER BY EMAIL
# ------------------------------------------------
@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email_route(
    email: str,
    db: Session = Depends(get_db)
):

    try:
        return get_user_by_email(
            db,
            email
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ------------------------------------------------
# LOGIN USER
# ------------------------------------------------
@router.post("/login", response_model=UserResponse)
def login_user_route(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):

    try:
        return login_user(
            db,
            login_data.email,
            login_data.password
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )


# ------------------------------------------------
# UPDATE USER
# ------------------------------------------------
@router.put("/{user_id}", response_model=UserResponse)
def update_user_route(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db)
):

    try:
        return update_user(
            db,
            user_id,
            user_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ------------------------------------------------
# DELETE USER
# ------------------------------------------------
@router.delete("/{user_id}")
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db)
):

    try:
        return delete_user(
            db,
            user_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )