from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class StudentBase(BaseModel):
    #user_id: int = Field(..., example=1)
    usn:str = Field(..., example="1RV17CS001")
    branch:str = Field(..., example="CSE")

class StudentCreate(StudentBase):
    usn: str = Field(..., example="1RV17CS001")
    branch: str = Field(..., example="CSE")

class StudentRead(StudentBase):
    usn: str = Field(..., example="1RV17CS001", read_only=True)
    branch: str = Field(..., example="CSE", read_only=True)
    model_config = ConfigDict(from_attributes=True)

class StudentUpdate(BaseModel):
    usn: Optional[str] = Field(None, example="1RV17CS001")
    branch: Optional[str] = Field(None, example="CSE")


    
class StudentOut(StudentRead):
    id: int = Field(..., example=1, read_only=True)
    model_config = ConfigDict(from_attributes=True)
