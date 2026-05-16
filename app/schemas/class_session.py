# =========================================================
# class_session_schema.py
# =========================================================

from datetime import date, time
from pydantic import BaseModel


class ClassSessionCreate(BaseModel):

    faculty_id: int
    subject_id: int

    semester: int   # ✅ NEW

    date: date

    start_time: time
    end_time: time

    batch: str
    section: str


class ClassSessionResponse(BaseModel):

    id: int

    faculty_id: int
    subject_id: int

    semester: int   # ✅ NEW

    date: date

    start_time: time
    end_time: time

    batch: str
    section: str

    class Config:
        from_attributes = True