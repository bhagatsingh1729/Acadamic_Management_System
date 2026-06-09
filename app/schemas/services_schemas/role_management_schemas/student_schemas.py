from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, Field
from typing import Optional
from app.schemas.response_schemas.base_response import UserBasicInfo

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


class BranchData(BaseModel):
    name: str
    branch_uid: str  # no id

# -----------------------------------------
# RESPONSE SCHEMA
# -----------------------------------------
class StudentResponse(BaseModel):
    id: int          
    usn: str
    semester: int
    batch: str
    section: str
    branch: BranchData
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)
