from fastapi import APIRouter, Depends
from app.crud.user_crud import create_user,update_user,get_all_users,get_user_by_email,get_user_by_id
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)

from app.crud.user_crud import (
    create_user,
    get_user_by_id,
    get_user_by_email,
    get_all_users,
    update_user,
    delete_user,
    read_users_by_role
)


router_user = APIRouter(prefix="/users",tags=["Users"])


@router_user.post("/",response_model=UserResponse,status_code=201)
def create_user_route(user_data: UserCreate,db: Session = Depends(get_db)):
    try:
        return create_user(
            db=db,
            user_data=user_data
        )
    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router_user.get("/{user_id}",response_model=UserResponse)
def get_user_route(user_id: int,db: Session = Depends(get_db)):
    user = get_user_by_id(db=db,user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user


@router_user.get("/email/{email}",response_model=UserResponse)
def get_user_email_route(email: str,db: Session = Depends(get_db)):

    user = get_user_by_email(db=db,email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@router_user.get("/get-users",response_model=list[UserResponse])
def get_all_users_route(skip: int = 0,limit: int = 100,db: Session = Depends(get_db)):
    return get_all_users(db=db,skip=skip,limit=limit)


@router_user.patch("/update-user/{user_id}",response_model=UserResponse)
def update_user_route(user_id: int,update_data: UserUpdate,db: Session = Depends(get_db)):
    try:
        return update_user(db=db,user_id=user_id,update_data=update_data)

    except ValueError as e:

        raise HTTPException(status_code=404,detail=str(e))
    
    
@router_user.delete("/delete-user/{user_id}")
def delete_user_route(user_id: int,db: Session = Depends(get_db)):

    try:

        return delete_user(db=db,user_id=user_id)

    except ValueError as e:

        raise HTTPException(status_code=404,detail=str(e))


@router_user.get("/get-users/{role}")
def get_user_by_role(role:str,db:Session = Depends(get_db)):

    return read_users_by_role(db=db,role=role)