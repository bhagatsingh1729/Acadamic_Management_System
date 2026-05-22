from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


# =========================================================
# USER DATA RESPONSE
# =========================================================

class SuperAdminUserData(BaseModel):

    id: int

    name: str

    email: EmailStr

    phone_no: Optional[str] = None

    dob: Optional[str] = None

    address: Optional[str] = None

    class Config:
        from_attributes = True


# =========================================================
# CREATE
# =========================================================

class SuperAdminCreate(BaseModel):

    name: str

    email: EmailStr

    password: str

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


# =========================================================
# UPDATE
# =========================================================

class SuperAdminUpdate(BaseModel):

    name: Optional[str] = None

    email: Optional[EmailStr] = None

    password: Optional[str] = None

    phone_no: Optional[str] = None

    dob: Optional[str] = None

    address: Optional[str] = None


# =========================================================
# RESPONSE
# =========================================================

class SuperAdminResponse(BaseModel):

    id: int

    user_id: int

    user: SuperAdminUserData

    class Config:
        from_attributes = True