from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EnrollmentRequest(BaseModel):
    usn: str
    code: str



class StudentSchema(BaseModel):
    usn: str
    model_config = ConfigDict(from_attributes=True)

class SubjectSchema(BaseModel):
    code: str
    model_config = ConfigDict(from_attributes=True)

class EnrollmentResponse(BaseModel):
    # This maps to the relationships in your model
    student: StudentSchema
    subject: SubjectSchema
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)