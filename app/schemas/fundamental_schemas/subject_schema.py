from pydantic import BaseModel
from typing import Optional


# ------------------------------------------------
# CREATE SUBJECT
# ------------------------------------------------
class SubjectCreate(BaseModel):
    name: str
    code: str
    semester: int


# ------------------------------------------------
# UPDATE SUBJECT
# ------------------------------------------------
class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    semester: Optional[int] = None


# ------------------------------------------------
# RESPONSE SCHEMA
# ------------------------------------------------
class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    semester: int

    class Config:
        orm_mode = True