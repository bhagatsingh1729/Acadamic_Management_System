from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

ExamType = Literal["INTERNAL", "MIDTERM", "FINAL", "QUIZ","IA1"]

class ExamCreateRequest(BaseModel):
    type: str
    subject_code: str = Field(..., examples=["CS301"])
    max_marks: int = Field(..., gt=0)
    semester: int = Field(..., gt=0)
    batch: str = Field(..., examples=["2024"])
    section: str = Field(..., examples=["DS-A"])  # ➕ Added section field
    date: date

class ExamResponse(BaseModel):
    type: str
    subject_code: str
    max_marks: int
    semester: int
    batch: str
    section: str  # ➕ Added section field
    date: date

    model_config = ConfigDict(from_attributes=True)