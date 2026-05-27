from pydantic import BaseModel,ConfigDict,field_validator
from typing import Optional


# -----------------------------------------
# CREATE DEPARTMENT
# -----------------------------------------
class DepartmentCreate(BaseModel):
    name: str
    dept_uid: str

    # Convert both fields to uppercase
    @field_validator("name", "dept_uid", mode="before")
    def to_upper(cls, value: str) -> str:
        return value.upper()

# -----------------------------------------
# UPDATE DEPARTMENT
# -----------------------------------------
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    dept_uid: Optional[str] = None

    @field_validator("name", "dept_uid", mode="before")
    def to_upper(cls, value: str) -> str:
        return value.upper() if value is not None else value

# -----------------------------------------
# RESPONSE SCHEMA
# -----------------------------------------
class DepartmentResponse(BaseModel):
    id: int
    name: str
    dept_uid: str

    model_config = ConfigDict(from_attributes=True)

    """
    @field_validator("name", "dept_uid", mode="before")
    def to_upper(cls, value: str) -> str:
        return value.upper()
    """

class MessageResponse(BaseModel):
    message:str