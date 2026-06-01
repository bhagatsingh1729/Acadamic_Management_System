# =============================================================
# schemas/services_schemas/super_admin_schemas/role_management.py
#
# Service-level request/response schemas for super_admin role management.
#
# FIXES APPLIED:
#   - Removed "from app.models.models import User, Branch"
#     Schema files must NEVER import DB models.
#   - AdminResponse.branch_id changed to Optional[int]
#     because Admin.branch_id is nullable in the DB model.
#   - FacultyResponse.dept_id changed to Optional[int]
#     because Faculty.dept_id is nullable in the DB model.
#   - Added PasswordChangeRequest schema for the
#     change-password endpoint (replaces query param).
# =============================================================

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
from typing import Optional

from app.schemas.response_schemas.base_response import UserBasicInfo


# =============================================================
# ADMIN SCHEMAS
# =============================================================

class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    branch_uid: str
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


class AdminUpdate(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    branch_uid: Optional[str] = None


class AdminResponse(BaseModel):
    id: int
    user_id: int
    branch_id: Optional[int] = None    # FIX: was int (non-optional) — DB allows NULL

    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# STUDENT SCHEMAS
# =============================================================

class StudentCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    usn: str
    semester: int = Field(..., ge=1, le=8)
    batch: str
    section: str = "A"
    branch_uid: str
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None


class StudentUpdateRequest(BaseModel):
    semester: Optional[int] = Field(None, ge=1, le=8)
    batch: Optional[str] = None
    section: Optional[str] = None
    branch_uid: Optional[str] = None   # super_admin can transfer student to another branch
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    user_id: int
    usn: str
    semester: int
    batch: str
    section: str
    branch_id: int
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)


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


# =============================================================
# USER SCHEMAS
# =============================================================

class PasswordChangeRequest(BaseModel):
    """
    FIX: new_password moved from query param to request body.
    Passwords must NEVER appear in URLs — they get logged
    by servers, proxies, and browsers.
    """
    new_password: str = Field(..., min_length=6)
