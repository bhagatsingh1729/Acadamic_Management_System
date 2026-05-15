from sqlalchemy.orm import Session
from app.utils.security import hash_password, verify_password
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate


# ------------------------------------------------
# CREATE USER
# ------------------------------------------------
def create_user(
    db: Session,
    user_data: UserCreate
):

    valid_roles = [
        "student",
        "faculty",
        "admin"
    ]

    # role validation
    if user_data.role not in valid_roles:
        raise ValueError("Invalid role")

    # email uniqueness
    existing_email = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_email:
        raise ValueError("Email already exists")

    # uid uniqueness
    existing_uid = (
        db.query(User)
        .filter(User.uid == user_data.uid)
        .first()
    )

    if existing_uid:
        raise ValueError("UID already exists")

    hashed_password = hash_password(
        user_data.password
    )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role,
        uid=user_data.uid,
        password=hashed_password,
        phone_no=user_data.phone_no,
        dob=user_data.dob,
        address=user_data.address
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ------------------------------------------------
# GET ALL USERS
# ------------------------------------------------
def get_all_users(db: Session):

    users = db.query(User).all()

    return users


# ------------------------------------------------
# GET USER BY ID
# ------------------------------------------------
def get_user_by_id(
    db: Session,
    user_id: int
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    return user


# ------------------------------------------------
# GET USER BY EMAIL
# ------------------------------------------------
def get_user_by_email(
    db: Session,
    email: str
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    return user


# ------------------------------------------------
# LOGIN USER
# ------------------------------------------------
def login_user(
    db: Session,
    email: str,
    password: str
):

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError("Invalid email or password")

    valid_password = verify_password(
        password,
        user.password
    )

    if not valid_password:
        raise ValueError("Invalid email or password")

    return user


# ------------------------------------------------
# UPDATE USER
# ------------------------------------------------
def update_user(
    db: Session,
    user_id: int,
    user_data: UserUpdate
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    # update email
    if user_data.email:

        existing_email = (
            db.query(User)
            .filter(
                User.email == user_data.email,
                User.id != user_id
            )
            .first()
        )

        if existing_email:
            raise ValueError("Email already exists")

        user.email = user_data.email

    # update optional fields
    if user_data.name:
        user.name = user_data.name

    if user_data.phone_no:
        user.phone_no = user_data.phone_no

    if user_data.dob:
        user.dob = user_data.dob

    if user_data.address:
        user.address = user_data.address

    db.commit()
    db.refresh(user)

    return user


# ------------------------------------------------
# DELETE USER
# ------------------------------------------------
def delete_user(
    db: Session,
    user_id: int
):

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    db.delete(user)
    db.commit()

    return {
        "message": "User deleted successfully"
    }