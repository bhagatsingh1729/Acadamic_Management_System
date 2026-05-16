# =========================================================
# exam_schema.py
# =========================================================

from datetime import date

from pydantic import BaseModel


class ExamCreate(BaseModel):

    type: str

    subject_id: int

    max_marks: int

    semester: int

    batch: str

    date: date


class ExamResponse(BaseModel):

    id: int

    type: str

    subject_id: int

    max_marks: int

    semester: int

    batch: str

    date: date

    class Config:
        from_attributes = True