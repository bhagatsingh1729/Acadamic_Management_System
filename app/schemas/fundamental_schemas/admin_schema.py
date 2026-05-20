from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


# =========================
# CREATE ADMIN
# =========================
class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    branch_id: int

    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):

        if len(value.strip()) < 2:
            raise ValueError("name too short")

        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if len(value) < 6:
            raise ValueError("password too short")

        return value
    
# =========================
# UPDATE ADMIN
# =========================
class AdminUpdate(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

    branch_id: Optional[int] = None

# =========================
# RESPONSE
# =========================
class AdminResponse(BaseModel):
    id: int
    user_id: int
    branch_id: int

    name: str
    email: EmailStr

    class Config:
        from_attributes = True