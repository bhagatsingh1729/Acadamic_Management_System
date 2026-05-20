# =========================================================
# marks_schema.py
# =========================================================

from pydantic import BaseModel


class MarksCreate(BaseModel):

    student_id: int

    exam_id: int

    score: int


class MarksResponse(BaseModel):

    id: int

    student_id: int

    exam_id: int

    score: int

    class Config:
        from_attributes = True