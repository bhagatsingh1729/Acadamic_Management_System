# =============================================================
# schemas/services_schemas/auth_schema.py
# =============================================================

from typing import Optional
from pydantic import BaseModel,EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str
    role: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
