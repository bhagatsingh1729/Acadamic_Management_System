from pydantic import BaseModel,EmailStr,Field
from typing import Annotated,Optional

class StudentBase(BaseModel):
    usn : str = Field(...,min_length=10,max_length=10)
    name : str = Field(...,min_length=2,max_length=100)
    email : EmailStr = Field(...)
    age : int = Field(...,ge=0)
    branch : str = Field(...,min_length=2,max_length=100)

class StudentCreate(StudentBase):
    password : str = Field(...,min_length=6,max_length=100)

class StudentUpdate(BaseModel):
    name : Optional[str] = Field(None,min_length=2,max_length=100)
    email : Optional[EmailStr] = Field(None)
    age : Optional[int] = Field(None,ge=0)
    branch : Optional[str] = Field(None,min_length=2,max_length=100)

class StudentDelete(BaseModel):
    usn : str = Field(...,min_length=10,max_length=10)
    
class StudentOut(StudentBase):
    id:int
    class Config:
        orm_mode = True
    