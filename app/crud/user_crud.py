from sqlalchemy.orm import Session
from app.models.models import User
from app.utils.utils import get_user
from app.schemas.user import (
    UserCreate,
    UserUpdate
)
from fastapi import HTTPException
from app.core.security import hash_password


#Create User
def create_user(db: Session,user_data: UserCreate) -> User:

    # ==========================================
    # Check email uniqueness
    # ==========================================

    existing_email = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_email:
        raise ValueError("Email already exists")

    # ==========================================
    # Check UID uniqueness
    # ==========================================

    existing_uid = (
        db.query(User)
        .filter(User.uid == user_data.uid)
        .first()
    )

    if existing_uid:
        raise ValueError("UID already exists")

    # ==========================================
    # Hash password
    # ==========================================

    hashed_password = hash_password(
        user_data.password
    )

    # ==========================================
    # Create ORM object
    # ==========================================

    db_user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role,
        uid=user_data.uid,
        password=hashed_password,
        phone_no=user_data.phone_no,
        dob=user_data.dob,
        address=user_data.address,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#Get user by user_id
def get_user_by_id(db: Session,user_id: int) -> User | None:

    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

# GET User via email
def get_user_by_email(db: Session,email: str) -> User | None:

    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


# GET All Users
def get_all_users(db: Session,skip: int = 0,limit: int = 100):

    return (
        db.query(User)
        .offset(skip)
        .limit(limit)
        .all()
    )

# Update User
def update_user(db: Session,user_id: int,update_data: UserUpdate) -> User:

    db_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not db_user:
        raise ValueError("User not found")

    # ==========================================
    # Convert only provided fields
    # ==========================================

    update_dict = update_data.model_dump(
        exclude_unset=True
    )
    print(f"DEBUG: Fields detected for update: {update_dict}")
    # ==========================================
    # Dynamically update fields
    # ==========================================

    for field, value in update_dict.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# Delete user via User_ID
def delete_user(db: Session,user_id: int):

    db_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not db_user:
        raise ValueError("User not found")

    db.delete(db_user)

    db.commit()

    return {
        "message": "User deleted successfully"
    }


# READ User via Role
def read_users_by_role(db:Session,role:str):
    if role.lower() in ["student","faculty","admin"]:
        user_db = db.query(User).filter(User.role == role).limit(100).all()
        if not user_db:
            raise HTTPException(status_code=404)
        return user_db
    raise HTTPException(status_code=500)