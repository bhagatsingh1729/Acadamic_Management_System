from pydantic import BaseModel, EmailStr, field_validator,ConfigDict
from typing import Optional
from app.models.models import User
from app.schemas.response_schemas.base_response import UserBasicInfo
# =========================
# CREATE ADMIN
# =========================
class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    branch_uid:str

    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):

        if len(value.strip()) < 2:
            raise ValueError("name too short")

        return value.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if len(value) < 6:
            raise ValueError("password too short")

        return value
    
# =========================
# UPDATE ADMIN
# =========================
class AdminUpdate(BaseModel):
    name: Optional[str] = None
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

    branch_uid: Optional[str] = None

# =========================
# RESPONSE
# =========================
class AdminResponse(BaseModel):
    id: int
    user_id: int
    branch_id: int

    user:UserBasicInfo
    model_config = ConfigDict(from_attributes=True)