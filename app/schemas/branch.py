from pydantic import BaseModel
from datetime import datetime


class BranchCreate(BaseModel):
    name: str
    branch_uid: str


class BranchUpdate(BaseModel):
    name: str | None = None
    branch_uid: str | None = None


class BranchResponse(BaseModel):
    id: int
    name: str
    branch_uid: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    