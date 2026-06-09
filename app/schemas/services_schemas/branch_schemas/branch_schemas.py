from pydantic import BaseModel,ConfigDict
from datetime import datetime


class BranchCreate(BaseModel):
    name: str
    branch_uid: str


class BranchUpdate(BaseModel):
    name: str | None = None
    branch_uid: str | None = None


#=============================================
# Response schema
#=============================================
class BranchResponse(BaseModel):
    id: int
    name: str
    branch_uid: str

    model_config = ConfigDict(from_attributes=True)