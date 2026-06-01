from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from app.schemas.response_schemas.base_response import UserBasicInfo


# =============================================================
# FACULTY SCHEMAS
# =============================================================

class FacultyCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    employee_id: str
    dept_uid: str
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if len(value.strip()) < 2:
            raise ValueError("Name too short — minimum 2 characters")
        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password too short — minimum 6 characters")
        return value


class FacultyUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    dept_uid: Optional[str] = None


class FacultyResponse(BaseModel):
    id: int
    employee_id: str
    dept_id: Optional[int] = None      # FIX: was int (non-optional) — DB allows NULL
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)
