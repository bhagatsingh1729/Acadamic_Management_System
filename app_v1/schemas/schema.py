from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class StudentBase(BaseModel):
    usn: str = Field(..., min_length=10, max_length=10)
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr = Field(...)
    age: int = Field(..., ge=1)  # ge=1 since age 0 makes no sense for a student
    branch: str = Field(..., min_length=2, max_length=100)


class StudentCreate(StudentBase):
    password: str = Field(..., min_length=6, max_length=100)


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = Field(None)
    age: Optional[int] = Field(None, ge=1)
    branch: Optional[str] = Field(None, min_length=2, max_length=100)


# Fix: removed StudentDelete — it was defined but never used anywhere


class StudentOut(StudentBase):
    # Fix: removed 'id: int' — the model has no 'id' column; 'usn' is the primary key
    # Fix: replaced deprecated 'class Config: orm_mode = True' with Pydantic v2 syntax
    model_config = ConfigDict(from_attributes=True)
