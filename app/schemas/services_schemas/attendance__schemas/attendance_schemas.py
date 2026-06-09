from pydantic import BaseModel,Field,ConfigDict
from typing import Optional,Literal,List

class AttendanceCreateRequest(BaseModel):
    student_name:str = Field(..., description="Name of the student")
    usn:str = Field(..., description="USN of the student")
    class_session_id:int = Field(..., description="ID of the class session")
    status:Optional[Literal["present", "absent"]] = Field(None, description="Attendance status")

class AttendanceResponse(BaseModel):
    student_name:str
    usn:str
    class_session_id:int
    subject_name:str
    status:Literal["present", "absent"]

    model_config = ConfigDict(from_attributes=True)


class BulkAttendanceItem(BaseModel):
    usn: str
    status: Literal["present", "absent"]

class AttendanceBulkMarkRequest(BaseModel):
    class_session_id: int
    records: List[BulkAttendanceItem]

#=============================================
# Response schema
#=============================================
class AttendanceSummaryResponse(BaseModel):
    usn: str
    student_name: str
    total_sessions: int
    attended_sessions: int
    attendance_percentage: float

    model_config = ConfigDict(from_attributes=True)

class StudentAttendanceResponse(BaseModel):
    usn: str
    student_name: str
    subject_name:str
    subject_code:str
    total_sessions: int
    attended_sessions: int
    attendance_percentage: float

    model_config = ConfigDict(from_attributes=True)