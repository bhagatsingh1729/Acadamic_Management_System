from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app_v2.database import get_db
from typing import List
from app_v2.models.models import User
from app_v2.schemas.user_schema import UserBase,UserCreate,UserRead,UserUpdate,UserOut
from app_v2.crud.user_crud import create_user, create_users_bulk,read_user,update_user,delete_user

router_user = APIRouter()

@router_user.post("/create-user",response_model=UserOut)
def create_user_route(user:UserCreate,db:Session = Depends(get_db)):
    return create_user(db, user)

@router_user.post("/create-users-bulk",response_model=List[UserOut])
def create_users_bulk_route(users: List[UserCreate], db:Session = Depends(get_db)):
    return create_users_bulk(db, users)

@router_user.get("/users",response_model=List[UserOut])
def read_users_route(db:Session = Depends(get_db)):
    return db.query(User).all()

@router_user.get("/user/{user_id}",response_model=UserOut)
def get_user_route(user_id:int,db:Session = Depends(get_db)):
    return read_user(user_id,db)

@router_user.put("/user-update/{user_id}",response_model=UserOut)
def update_user_route(user_id:int, user: UserUpdate, db:Session = Depends(get_db)):
    return update_user(db, user_id, user)

#could you suggest a better functions for the above one 
@router_user.delete("/user-delete/{user_id}",response_model=UserOut)
def delete_user_route(user_id:int,db:Session = Depends(get_db)):
    return delete_user(db,user_id)

#is the above code correct or do you suggest any changes?


