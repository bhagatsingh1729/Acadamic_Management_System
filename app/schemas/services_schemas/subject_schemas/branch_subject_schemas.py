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

"""
            User.name.label("faculty_name"),
            Faculty.employee_id.label("employee_id"),    # Added employee_id
            Department.name.label("dept_name"),          # Added dept_name
            Subject.name.label("subject_name"),
            Subject.code.label("subject_code")
"""

class BranchSubjectFacultyResponse(BaseModel):
    faculty_name:str
    employee_id:str
    dept_name:str
    subject_name:str
    subject_code:str