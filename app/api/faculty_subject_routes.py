from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db

from app.schemas.faculty_subject_schema import (
    FacultySubjectCreate,
    FacultySubjectResponse
)

from app.crud.faculty_subject_crud import (
    assign_subject_to_faculty,
    get_all_faculty_subjects,
    get_subjects_of_faculty,
    get_faculty_of_subject,
    delete_faculty_subject
)


router = APIRouter(
    prefix="/faculty-subject",
    tags=["Faculty Subject"]
)


# =========================
# ASSIGN SUBJECT TO FACULTY
# =========================
@router.post("/",response_model=FacultySubjectResponse)
def assign_subject_to_faculty_route(
    data: FacultySubjectCreate,
    db: Session = Depends(get_db)
):

    return assign_subject_to_faculty(
        db,
        data
    )


# =========================
# GET ALL MAPPINGS
# =========================
@router.get("/",response_model=List[FacultySubjectResponse])
def get_all_faculty_subjects_route(
    db: Session = Depends(get_db)
):

    return get_all_faculty_subjects(db)


# =========================
# GET SUBJECTS OF FACULTY
# =========================
@router.get("/faculty/{faculty_id}")
def get_subjects_of_faculty_route(
    faculty_id: int,
    db: Session = Depends(get_db)
):

    return get_subjects_of_faculty(
        db,
        faculty_id
    )


# =========================
# GET FACULTY OF SUBJECT
# =========================
@router.get("/subject/{subject_id}")
def get_faculty_of_subject_route(
    subject_id: int,
    db: Session = Depends(get_db)
):

    return get_faculty_of_subject(
        db,
        subject_id
    )


# =========================
# DELETE MAPPING
# =========================
@router.delete("/{mapping_id}")
def delete_faculty_subject_route(
    mapping_id: int,
    db: Session = Depends(get_db)
):

    return delete_faculty_subject(
        db,
        mapping_id
    )