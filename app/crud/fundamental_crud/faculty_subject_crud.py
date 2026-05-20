from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import (
    Faculty,
    Subject,
    FacultySubject
)

from app.schemas.fundamental_schemas.faculty_subject_schema import (
    FacultySubjectCreate
)


# =========================
# ASSIGN SUBJECT TO FACULTY
# =========================
def assign_subject_to_faculty(
    db: Session,
    data: FacultySubjectCreate
):

    # -------------------------
    # validate faculty
    # -------------------------
    faculty = (
        db.query(Faculty)
        .filter(Faculty.id == data.faculty_id)
        .first()
    )

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="faculty not found"
        )

    # -------------------------
    # validate subject
    # -------------------------
    subject = (
        db.query(Subject)
        .filter(Subject.id == data.subject_id)
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    # -------------------------
    # duplicate check
    # -------------------------
    existing_mapping = (
        db.query(FacultySubject)
        .filter(
            FacultySubject.faculty_id == data.faculty_id,
            FacultySubject.subject_id == data.subject_id
        )
        .first()
    )

    if existing_mapping:
        raise HTTPException(
            status_code=400,
            detail="subject already assigned to faculty"
        )

    # -------------------------
    # create mapping
    # -------------------------
    new_mapping = FacultySubject(
        faculty_id=data.faculty_id,
        subject_id=data.subject_id
    )

    db.add(new_mapping)

    db.commit()
    db.refresh(new_mapping)

    return new_mapping


# =========================
# GET ALL MAPPINGS
# =========================
def get_all_faculty_subjects(db: Session):

    mappings = db.query(FacultySubject).all()

    return mappings


# =========================
# GET SUBJECTS OF FACULTY
# =========================
def get_subjects_of_faculty(
    db: Session,
    faculty_id: int
):

    faculty = (
        db.query(Faculty)
        .filter(Faculty.id == faculty_id)
        .first()
    )

    if not faculty:
        raise HTTPException(
            status_code=404,
            detail="faculty not found"
        )

    return faculty.subjects


# =========================
# GET FACULTY OF SUBJECT
# =========================
def get_faculty_of_subject(
    db: Session,
    subject_id: int
):

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise HTTPException(
            status_code=404,
            detail="subject not found"
        )

    return subject.faculty_members


# =========================
# DELETE MAPPING
# =========================
def delete_faculty_subject(
    db: Session,
    mapping_id: int
):

    mapping = (
        db.query(FacultySubject)
        .filter(FacultySubject.id == mapping_id)
        .first()
    )

    if not mapping:
        raise HTTPException(
            status_code=404,
            detail="mapping not found"
        )

    db.delete(mapping)

    db.commit()

    return {
        "message": "mapping deleted successfully"
    }