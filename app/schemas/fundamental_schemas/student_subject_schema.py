# =========================================================
# student_subject_schema.py
# =========================================================

from pydantic import BaseModel


class StudentSubjectCreate(BaseModel):

    student_id: int
    subject_id: int


class StudentSubjectResponse(BaseModel):

    id: int

    student_id: int
    subject_id: int

    class Config:
        from_attributes = True