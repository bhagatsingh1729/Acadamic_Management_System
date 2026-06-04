from datetime import date
from typing import Literal
from pydantic import BaseModel,Field,ConfigDict

class ExamCreateRequest(BaseModel):

    type:str
    subject_code:str
    max_marks:int
    semester:int
    batch:str
    date:date


class ExamResponse(BaseModel):

    type: str

    subject_code: str

    max_marks: int

    semester: int

    batch: str

    date: date

    model_config = ConfigDict(from_attributes=True)
