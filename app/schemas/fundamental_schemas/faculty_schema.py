from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


# =========================
# CREATE FACULTY
# =========================
class FacultyCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    employee_id: str
    dept_id: int

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
# UPDATE FACULTY
# =========================
class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    dept_id: Optional[int] = None


# =========================
# RESPONSE
# =========================
class FacultyResponse(BaseModel):
    id: int
    employee_id: str
    dept_id: int

    user_id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True