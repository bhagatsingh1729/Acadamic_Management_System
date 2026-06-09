from pydantic import BaseModel,ConfigDict,Field
from typing import Optional

class AssignMarksRequest(BaseModel):
    usn:str
    exam_id:int
    score: int = Field(...,ge=0,le=100)


# -----------------------------------------
# RESPONSE SCHEMA
# -----------------------------------------
class AssignMarksResponse(BaseModel):
    id:int
    usn:str
    exam_id:int
    subject_code:str
    score: int = Field(...,ge=0,le=100)

    model_config = ConfigDict(from_attributes=True)