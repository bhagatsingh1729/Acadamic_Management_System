from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date,time
class ClassSessionCreateRequest(BaseModel):
    faculty_name:str
    employee_id:str
    code:str

    semester:int

    date:date

    start_time:time
    end_time:time
    batch:str
    section:str


#=============================================
# Response schema
#=============================================
class ClassSessionResponse(BaseModel):
    session_id:int
    faculty_name:str
    employee_id:str
    code:str

    semester:int

    date:date
    
    start_time:time
    end_time:time
    batch:str
    section:str

    model_config = ConfigDict(from_attributes=True)