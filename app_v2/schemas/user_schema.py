from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8)
    role: str = Field(..., example="student")

class UserCreate(UserBase):
    pass

class UserRead(BaseModel):
    id: int
    email: EmailStr
    role: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, example="user@example.com")
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[str] = Field(None, example="student")

class UserOut(UserRead):
    id: int = Field(..., example=1, read_only=True)
    model_config = ConfigDict(from_attributes=True)


"""    # Fix: replaced deprecated 'class Config: orm_mode = True' with Pydantic v2 syntax
        model_config = ConfigDict(from_attributes=True)
"""

