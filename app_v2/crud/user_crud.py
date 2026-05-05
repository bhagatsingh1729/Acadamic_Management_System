from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app_v2.models.models import User
from app_v2.schemas.user_schema import UserBase,UserCreate,UserRead,UserUpdate,UserOut
from app_v2.core.security import hash_password

def create_user(db:Session,user:UserCreate) -> User:
    db_user = User(
        email = user.email,
        password = user.password,
        role = user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def read_user(user_id:int, db:Session) -> UserOut:
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        return db_user
    raise HTTPException(status_code=404,detail="user not found")

def update_user(db:Session, user_id:int, user:UserUpdate) -> UserOut:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="user not found")
    if user.email is not None:
        db_user.email = user.email
    if user.password is not None:
        db_user.password = user.password
    if user.role is not None:
        db_user.role = user.role
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db:Session,user_id:int) -> UserOut:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="user not found")
    db.delete(db_user)
    db.commit()
    return db_user

#check if all the code is correct and suggest changes if any:

        
