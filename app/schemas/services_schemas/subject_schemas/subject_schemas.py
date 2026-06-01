from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ------------------------------------------------
# CREATE SUBJECT
# ------------------------------------------------
class SubjectCreateRequest(BaseModel):
    name: str
    code: str
    semester: int
    credits: int = Field(..., gt=0, le=12)


# ------------------------------------------------
# UPDATE SUBJECT
# ------------------------------------------------
class SubjectUpdateRequest(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)