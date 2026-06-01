from pydantic import BaseModel,ConfigDict


# =========================
# CREATE MAPPING
# =========================
class BranchSubjectCreate(BaseModel):
    branch_id: int
    subject_id: int


# =========================
# RESPONSE
# =========================
class BranchSubjectResponse(BaseModel):
    id: int

    branch_id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)