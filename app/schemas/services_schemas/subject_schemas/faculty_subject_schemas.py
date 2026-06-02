from pydantic import BaseModel,ConfigDict

class FacultySubjectRequest(BaseModel):
    employee_id:str
    code:str

class FacultySchema(BaseModel):
    employee_id:str
    model_config = ConfigDict(from_attributes=True)

class SubjectSchema(BaseModel):
    code:str
    model_config = ConfigDict(from_attributes=True)

class FacultySubjectResponse(BaseModel):
    employee_id:FacultySchema
    code:SubjectSchema

    model_config = ConfigDict(from_attributes=True)