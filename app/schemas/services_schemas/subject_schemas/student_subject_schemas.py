from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.services_schemas.role_management_schemas.student_schemas import StudentResponse

class EnrollmentRequest(BaseModel):
    usn: str
    code: str

class SubjectData(BaseModel):
    id: int #subject id
    name: str #subject name
    code: str #subject code
    semester: int
    credits: int

    model_config = ConfigDict(from_attributes=True)

#----------------------------------------------------
# Response Schema
#----------------------------------------------------
class EnrollmentResponse(BaseModel):
    usn:str
    subject:SubjectData
    
    model_config = ConfigDict(from_attributes=True)