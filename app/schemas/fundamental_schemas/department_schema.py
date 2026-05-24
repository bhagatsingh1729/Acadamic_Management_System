from pydantic import BaseModel,ConfigDict
from typing import Optional


# -----------------------------------------
# CREATE DEPARTMENT
# -----------------------------------------
class DepartmentCreate(BaseModel):
    name: str
    dept_uid: str


# -----------------------------------------
# UPDATE DEPARTMENT
# -----------------------------------------
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    dept_uid: Optional[str] = None


# -----------------------------------------
# RESPONSE SCHEMA
# -----------------------------------------
class DepartmentResponse(BaseModel):
    id: int
    name: str
    dept_uid: str

    model_config = ConfigDict(from_attributes=True)