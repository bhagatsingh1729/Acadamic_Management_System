from pydantic import BaseModel, EmailStr, field_validator,ConfigDict,Field
from typing import Optional
from app.models.models import User,Branch
from app.schemas.response_schemas.base_response import UserBasicInfo
# =========================
# CREATE ADMIN
# =========================
class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    branch_uid:str

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

    branch_uid: Optional[str] = None

# =========================
# RESPONSE
# =========================
class AdminResponse(BaseModel):
    id: int
    user_id: int
    branch_id: int

    user:UserBasicInfo 
    model_config = ConfigDict(from_attributes=True)


#===============================
# Student Schemas
#===============================

class StudentCreateRequest(BaseModel):
    """
    What the admin sends when creating a student.
    Uses branch_uid (human-friendly) instead of branch_id (DB int).
    The service resolves branch_uid to branch_id internally.
    """
    # User fields
    name: str
    email: EmailStr
    password: str = Field(..., min_length=8)

    # Student-specific fields
    usn: str
    semester: int = Field(..., ge=1, le=8)
    batch: str                      # e.g. "2023-27"
    section: str = "A"              # e.g. "A", "B", "C"

    # Human-friendly identifier — NOT the DB integer id
    branch_uid: str                 # e.g. "CSE", "ECE"

    # Optional personal info
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None


class StudentUpdateRequest(BaseModel):
    """
    What admin sends when updating a student.
    Only includes fields that are safe to update.
    """
    semester: Optional[int] = Field(None, ge=1, le=8)
    batch: Optional[str] = None
    section: Optional[str] = None
    branch_uid:Optional[str] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

# =============================================================
# STUDENT RESPONSE
# =============================================================
class StudentResponse(BaseModel):
    id: int
    user_id: int
    usn: str
    semester: int
    batch: str
    section: str
    branch_id: int
    #branch_uid:str # Adding this get branch_uid
    #branch:Branch
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)

#===========================================
# Faculty Schema
#===========================================

# =========================
# CREATE FACULTY
# =========================
class FacultyCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    employee_id: str
    dept_uid:str

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
class FacultyUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    dept_uid: Optional[str] = None

# =========================
# RESPONSE
# =========================
class FacultyResponse(BaseModel):
    id: int
    employee_id: str
    dept_id: int

    user:UserBasicInfo

    model_config = ConfigDict(from_attributes=True)