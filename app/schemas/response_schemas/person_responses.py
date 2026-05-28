# =============================================================
# schemas/response_schemas/person_responses.py
#
# Response schemas for all role-based entities.
# Every schema uses nested UserBasicInfo to carry name/email.
# =============================================================
#
# HOW NESTING WORKS (important to understand):
#
#   Faculty model (DB):
#       id, user_id, employee_id, dept_id
#       + relationship: user → User object
#
#   FacultyResponse (this file):
#       id, employee_id, dept_id
#       user: UserBasicInfo  ← Pydantic reads faculty.user automatically
#
#   When FastAPI serializes a Faculty ORM object:
#       faculty.id          → FacultyResponse.id
#       faculty.employee_id → FacultyResponse.employee_id
#       faculty.dept_id     → FacultyResponse.dept_id
#       faculty.user.name   → FacultyResponse.user.name   ✅
#       faculty.user.email  → FacultyResponse.user.email  ✅
#
# =============================================================

from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.response_schemas.base_response import UserBasicInfo


# =============================================================
# SUPER ADMIN RESPONSE
# =============================================================
class SuperAdminResponse(BaseModel):
    id: int
    user_id: int
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# ADMIN RESPONSE
# =============================================================
class AdminResponse(BaseModel):
    id: int
    user_id: int
    branch_id: Optional[int] = None
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# HOD RESPONSE
# =============================================================
class HodResponse(BaseModel):
    id: int
    user_id: int
    department_id: int
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# FACULTY RESPONSE
# =============================================================
class FacultyResponse(BaseModel):
    id: int
    user_id: int
    employee_id: str
    dept_id: Optional[int] = None
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)


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
