from pydantic import BaseModel,ConfigDict

class FacultySubjectRequest(BaseModel):
    employee_id:str
    code:str


class SubjectData(BaseModel):
    name:str
    code:str
    semester:int
    credits:int

    model_config = ConfigDict(from_attributes=True)

class FacultySubjectResponse(BaseModel):
    employee_id:str
    subject:SubjectData

    model_config = ConfigDict(from_attributes=True)