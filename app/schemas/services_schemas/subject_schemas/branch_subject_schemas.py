from pydantic import BaseModel,ConfigDict
from typing import Optional
from app.schemas.services_schemas.subject_schemas.subject_schemas import SubjectResponse
class BranchSubjectCreateRequest(BaseModel):
    branch_uid:str
    code:str

class BranchSubjectUpdateRequest(BaseModel):
    branch_uid:Optional[str] | None
    code:Optional[str] | None

class MappingResponse(BaseModel):


    branch_uid: str
    code: str

    model_config = ConfigDict(from_attributes=True)

class Branch_Subjects_response(BaseModel):

    name: str
    code: str
    semester: int
    credits: int

    model_config = ConfigDict(from_attributes=True)
