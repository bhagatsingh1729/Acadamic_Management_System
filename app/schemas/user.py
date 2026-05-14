from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ============================================================
# BASE USER SCHEMA
# ============================================================

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

    email: EmailStr

    role: str

    phone_no: Optional[str] = None

    address: Optional[str] = None


# ============================================================
# CREATE USER
# ============================================================
# password only needed during creation
# NEVER return password in response schemas
# ============================================================

class UserCreate(UserBase):
    uid: str

    password: str = Field(..., min_length=8)

    dob: Optional[str] = None


# ============================================================
# UPDATE USER
# ============================================================
# all optional because PATCH-like behavior
# ============================================================

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)

    phone_no: Optional[str] = Field(None, max_length=13)

    address: Optional[str] = Field(None)

    dob: Optional[str] = Field(None,examples=["01-01-1998"])


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(UserBase):
    id: int

    uid: str

    dob: Optional[str]

    created_at: datetime

    updated_at: datetime

    class Config:
        from_attributes = True