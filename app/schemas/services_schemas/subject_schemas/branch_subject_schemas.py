from pydantic import BaseModel, ConfigDict
from typing import Optional

class BranchSubjectCreateRequest(BaseModel):
    branch_uid: str
    code: str

class BranchSubjectUpdateRequest(BaseModel):
    branch_uid: Optional[str] = None
    code: Optional[str] = None

class SubjectData(BaseModel):
    id: int 
    name: str 
    code: str 
    semester: int
    credits: int

    model_config = ConfigDict(from_attributes=True)

class MappingResponse(BaseModel):
    branch_uid: str
    subject: SubjectData # Nested subject object

    model_config = ConfigDict(from_attributes=True)