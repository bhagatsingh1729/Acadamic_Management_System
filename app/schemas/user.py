from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# ------------------------------------------------
# CREATE USER
# ------------------------------------------------
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str
    password: str = Field(..., min_length=8, max_length=128)

    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None


# ------------------------------------------------
# UPDATE USER
# ------------------------------------------------
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None


# ------------------------------------------------
# LOGIN
# ------------------------------------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ------------------------------------------------
# RESPONSE SCHEMA
# ------------------------------------------------
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    phone_no: Optional[str]
    dob: Optional[str]
    address: Optional[str]

    class Config:
        from_attributes = True