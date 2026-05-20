# =========================================================
# hod_schema.py
# =========================================================

from pydantic import BaseModel
from pydantic import EmailStr


class HodCreate(BaseModel):

    name: str
    email: EmailStr
    password: str

    department_id: int

    #employee_id: str


class HodResponse(BaseModel):

    id: int

    user_id: int
    department_id: int

    #employee_id: str

    class Config:
        from_attributes = True