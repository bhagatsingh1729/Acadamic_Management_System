from pydantic import BaseModel, Field
from typing import Optional


# ------------------------------------------------
# CREATE SUBJECT
# ------------------------------------------------
class SubjectCreate(BaseModel):
    name: str
    code: str
    semester: int
    credits: int = Field(..., gt=0, le=12)


# ------------------------------------------------
# UPDATE SUBJECT
# ------------------------------------------------
class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    semester: Optional[int] = None
    credits: Optional[int] = None

# ------------------------------------------------
# RESPONSE SCHEMA
# ------------------------------------------------
class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    semester: int
    credits: int

    class Config:
        orm_mode = True