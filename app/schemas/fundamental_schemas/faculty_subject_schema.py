from pydantic import BaseModel


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

    class Config:
        from_attributes = True