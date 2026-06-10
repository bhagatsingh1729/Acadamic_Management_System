from datetime import date
from pydantic import BaseModel, ConfigDict

class ExamCreate(BaseModel):
    type: str 
    subject_id: int
    max_marks: int
    semester: int
    batch: str
    section: str  # ➕ Added section to prevent field stripping
    date: date

class ExamResponse(BaseModel):
    id: int
    type: str
    subject_id: int
    max_marks: int
    semester: int
    batch: str
    section: str  # ➕ Added section to the internal response mapping
    date: date

    model_config = ConfigDict(from_attributes=True)