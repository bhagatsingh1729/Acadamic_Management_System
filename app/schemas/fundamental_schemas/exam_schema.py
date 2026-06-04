# =========================================================
# exam_schema.py
# =========================================================

from datetime import date
from typing import Literal
from pydantic import BaseModel,Field,ConfigDict


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

    model_config = ConfigDict(from_attributes=True)