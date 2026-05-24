# =============================================================
# schemas/response_schemas/academic_responses.py
#
# Response schemas for non-person academic entities.
# These don't need nested UserBasicInfo since they have
# no User relationship.
# =============================================================

from datetime import date, time
from typing import Optional
from pydantic import BaseModel, ConfigDict


# =============================================================
# BRANCH RESPONSE
# =============================================================
class BranchResponse(BaseModel):
    id: int
    name: str
    branch_uid: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# DEPARTMENT RESPONSE
# =============================================================
class DepartmentResponse(BaseModel):
    id: int
    name: str
    dept_uid: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# SUBJECT RESPONSE
# =============================================================
class SubjectResponse(BaseModel):
    id: int
    name: str
    code: str
    semester: int
    credits: int

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# BRANCH-SUBJECT MAPPING RESPONSE
# =============================================================
class BranchSubjectResponse(BaseModel):
    id: int
    branch_id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# FACULTY-SUBJECT MAPPING RESPONSE
# =============================================================
class FacultySubjectResponse(BaseModel):
    id: int
    faculty_id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# STUDENT-SUBJECT MAPPING RESPONSE
# =============================================================
class StudentSubjectResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# CLASS SESSION RESPONSE
# =============================================================
class ClassSessionResponse(BaseModel):
    id: int
    faculty_id: int
    subject_id: int
    semester: int
    date: date
    start_time: time
    end_time: time
    batch: str
    section: str

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# ATTENDANCE RESPONSE
# =============================================================
class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    class_session_id: int
    status: int   # 1 = present, 0 = absent

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# EXAM RESPONSE
# =============================================================
class ExamResponse(BaseModel):
    id: int
    type: str
    subject_id: int
    max_marks: int
    semester: int
    batch: str
    date: date

    model_config = ConfigDict(from_attributes=True)


# =============================================================
# MARKS RESPONSE
# =============================================================
class MarksResponse(BaseModel):
    id: int
    student_id: int
    exam_id: int
    score: int

    model_config = ConfigDict(from_attributes=True)
