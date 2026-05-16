from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    student_id: int
    class_session_id: int
    status: int   # 1 = present, 0 = absent


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    class_session_id: int
    status: int

    class Config:
        from_attributes = True