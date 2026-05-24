# =============================================================
# schemas/response_schemas/base_response.py
#
# Shared base schemas used inside other response schemas.
# =============================================================
# WHY THIS FILE EXISTS:
#
# Every person in the system (Student, Faculty, Admin, HOD,
# SuperAdmin) has their core info (name, email, phone) stored
# in the User table — NOT in the role-specific table.
#
# So when we return a Faculty object in an API response,
# we can't just read Faculty.name — it doesn't exist there.
# We have to walk the relationship: faculty.user.name
#
# Pydantic handles this automatically with nested schemas
# IF we set model_config = ConfigDict(from_attributes=True)
# on BOTH the inner and outer schema.
#
# Pattern:
#   class FacultyResponse(BaseModel):
#       id: int
#       employee_id: str
#       user: UserBasicInfo   ← Pydantic walks faculty.user automatically
# =============================================================

from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBasicInfo(BaseModel):
    """
    Embedded inside every person-type response schema.
    Carries the User table fields that all roles share.
    Never returned alone — always nested inside a role response.
    """
    id: int
    name: str
    email: EmailStr
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

    # from_attributes=True tells Pydantic:
    # "read values from ORM object attributes, not a dict"
    model_config = ConfigDict(from_attributes=True)
