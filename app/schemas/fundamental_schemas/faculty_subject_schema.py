from pydantic import BaseModel,ConfigDict


# =========================
# CREATE MAPPING
# =========================
class FacultySubjectCreate(BaseModel):
    faculty_id: int
    subject_id: int


# =========================
# RESPONSE
# =========================
class FacultySubjectResponse(BaseModel):
    id: int

    faculty_id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)