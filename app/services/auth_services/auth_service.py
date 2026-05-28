from sqlalchemy.orm import Session
from app.models.models import User


from app.core.security import verify_password
from app.schemas.services_schemas.auth_schemas.auth_schema import LoginSchema, TokenResponseSchema 
from app.core.security import create_access_token


def login_user(
    db: Session,
    data: LoginSchema
) -> TokenResponseSchema:

    user = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if not user:
        raise ValueError(
            "invalid email or password"
        )

    password_valid = verify_password(
        data.password,
        user.password
    )

    if not password_valid:
        raise ValueError(
            "invalid email or password"
        )

    access_token = create_access_token(
        data={
            "user_id": user.id,
            "role": user.role
        }
    )

    return TokenResponseSchema(
        access_token=access_token,
        token_type="bearer",
        role=user.role
    )