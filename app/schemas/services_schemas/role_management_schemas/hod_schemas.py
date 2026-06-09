from pydantic import BaseModel,ConfigDict,EmailStr
from typing import Optional
from app.schemas.response_schemas.base_response import UserBasicInfo
class CreateHodRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    dept_uid:str

        # Optional personal info
    phone_no: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None

class DepartmentData(BaseModel):
    name:str
    dept_uid:str

    model_config = ConfigDict(from_attributes=True)

# =============================================================
# HOD RESPONSE
# =============================================================
class HodAccountResponse(BaseModel):
    id: int

    department:DepartmentData
    user: UserBasicInfo

    model_config = ConfigDict(from_attributes=True)