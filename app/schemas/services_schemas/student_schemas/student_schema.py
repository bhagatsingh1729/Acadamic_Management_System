# =============================================================
# schemas/services_schemas/student_schema.py
#
# Service-level request schemas for student operations.
# =============================================================
#
# WHY SEPARATE FROM fundamental_schemas/student_schema.py?
#
# fundamental_schemas/student_schema.py → StudentCreate uses branch_id (int)
#    This is what CRUD understands — raw DB IDs.
#
# services_schemas/student_schema.py → StudentCreateRequest uses branch_uid (str)
#    This is what the service/route accepts — human-friendly identifiers.
#    The service resolves branch_uid → branch_id before calling CRUD.
#
# The admin doesn't know that CSE branch has id=3 in the database.
# They know it as branch_uid="CSE" or "CSE_2023".
# =============================================================

from typing import Optional
from pydantic import BaseModel, EmailStr, Field,ConfigDict
from app.schemas.response_schemas.base_response import UserBasicInfo

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
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)

