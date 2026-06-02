# =========================================================
# student_subject_schema.py
# =========================================================

from pydantic import BaseModel,ConfigDict


class StudentSubjectCreate(BaseModel):

    student_id: int
    subject_id: int


class StudentSubjectResponse(BaseModel):

    id: int

    student_id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)