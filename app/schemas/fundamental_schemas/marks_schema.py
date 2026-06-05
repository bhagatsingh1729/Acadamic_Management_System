# =========================================================
# marks_schema.py
# =========================================================

from pydantic import BaseModel,ConfigDict,Field


class MarksCreate(BaseModel):

    student_id: int

    exam_id: int

    score: int = Field(...,gt=1,lt=101)


class MarksResponse(BaseModel):

    id: int

    student_id: int

    exam_id: int

    score: int

    model_config = ConfigDict(from_attributes=True)