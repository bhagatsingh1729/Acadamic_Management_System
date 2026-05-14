from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app_v2.models.models import User,Student,Faculty,Admin
from app_v2.schemas.user_schema import UserBase,UserCreate,UserRead,UserUpdate,UserOut
from app_v2.core.security import hash_password

def create_user(db:Session,user:UserCreate) -> User:
    # Check if user with this email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Hash the password
    hashed_password = hash_password(user.password)
    
    db_user = User(
        email = user.email,
        password = hashed_password,
        role = user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    if db_user.role == "student":
        # Create corresponding student record
        student = Student(user_id=db_user.id)
        db.add(student)
        db.commit()
    elif db_user.role == "faculty":
        # Create corresponding faculty record
        faculty = Faculty(user_id=db_user.id)
        db.add(faculty)
        db.commit()
    elif db_user.role == "admin":
        # Create corresponding admin record
        admin = Admin(user_id=db_user.id)
        db.add(admin)
        db.commit()
    return db_user

def create_users_bulk(db: Session, users: List[UserCreate]) -> List[User]:
    db_users = []
    for user in users:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail=f"User with email {user.email} already exists")
        if user.role not in ["student", "faculty", "admin"]:
            raise HTTPException(status_code=400, detail=f"Invalid role {user.role} for user with email {user.email}")
        
        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email,
            password=hashed_password,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db_users.append(db_user)

        if db_user.role == "student":
            student = Student(user_id=db_user.id)
            db.add(student)
            db.commit()
        elif db_user.role == "faculty":
            faculty = Faculty(user_id=db_user.id)
            db.add(faculty)
            db.commit()
        elif db_user.role == "admin":
            admin = Admin(user_id=db_user.id)
            db.add(admin)
            db.commit()
    
    return db_users


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

    if db_user.role == "student":
        # Delete corresponding student record
        db.query(Student).filter(Student.user_id == db_user.id).delete()
    elif db_user.role == "faculty":
        # Delete corresponding faculty record
        db.query(Faculty).filter(Faculty.user_id == db_user.id).delete()
    elif db_user.role == "admin":
        # Delete corresponding admin record
        db.query(Admin).filter(Admin.user_id == db_user.id).delete()
    
    db.commit()
    return db_user

#check if all the code is correct and suggest changes if any:

        
