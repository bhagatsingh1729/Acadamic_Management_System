from typing import Optional

from pydantic import BaseModel, Field


class StudentCreate(BaseModel):
    name: str
    email: str
    password: str = Field(..., min_length=8, max_length=64)

    usn: str

    semester: int = Field(..., ge=1, le=8)

    batch: str
    section: str 

    branch_id: int 

    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None


class StudentUpdate(BaseModel):
    semester: Optional[int] = Field(None, ge=1, le=8)

    batch: Optional[str] = None
    section: Optional[str] = None

    branch_id: Optional[int] = None

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

    class Config:
        from_attributes = True