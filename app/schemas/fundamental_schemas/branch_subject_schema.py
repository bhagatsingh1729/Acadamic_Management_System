from pydantic import BaseModel


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

    class Config:
        from_attributes = True