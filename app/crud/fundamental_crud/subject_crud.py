from sqlalchemy.orm import Session

from app.models.models import Subject

from app.schemas.fundamental_schemas.subject_schema import (
    SubjectCreate,
    SubjectUpdate
)


# ------------------------------------------------
# CREATE SUBJECT
# ------------------------------------------------
def create_subject(
    db: Session,
    subject_data: SubjectCreate
):

    # semester validation
    if subject_data.semester < 1 or subject_data.semester > 8:
        raise ValueError("Semester must be between 1 and 8")

    # check subject name uniqueness
    existing_subject = (
        db.query(Subject)
        .filter(Subject.name == subject_data.name)
        .first()
    )

    if existing_subject:
        raise ValueError("Subject name already exists")

    # check subject code uniqueness
    existing_code = (
        db.query(Subject)
        .filter(Subject.code == subject_data.code)
        .first()
    )

    if existing_code:
        raise ValueError("Subject code already exists")

    new_subject = Subject(
        name=subject_data.name,
        code=subject_data.code,
        semester=subject_data.semester
    )

    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)

    return new_subject


# ------------------------------------------------
# GET ALL SUBJECTS
# ------------------------------------------------
def get_all_subjects(db: Session):

    subjects = db.query(Subject).all()

    return subjects


# ------------------------------------------------
# GET SUBJECT BY ID
# ------------------------------------------------
def get_subject_by_id(
    db: Session,
    subject_id: int
):

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise ValueError("Subject not found")

    return subject


# ------------------------------------------------
# GET SUBJECT BY CODE
# ------------------------------------------------
def get_subject_by_code(
    db: Session,
    subject_code: str
):

    subject = (
        db.query(Subject)
        .filter(Subject.code == subject_code)
        .first()
    )

    if not subject:
        raise ValueError("Subject not found")

    return subject


# ------------------------------------------------
# GET SUBJECTS BY SEMESTER
# ------------------------------------------------
def get_subjects_by_semester(
    db: Session,
    semester: int
):

    if semester < 1 or semester > 8:
        raise ValueError("Semester must be between 1 and 8")

    subjects = (
        db.query(Subject)
        .filter(Subject.semester == semester)
        .all()
    )

    return subjects


# ------------------------------------------------
# UPDATE SUBJECT
# ------------------------------------------------
def update_subject(
    db: Session,
    subject_id: int,
    subject_data: SubjectUpdate
):

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise ValueError("Subject not found")

    # update name
    if subject_data.name:

        existing_name = (
            db.query(Subject)
            .filter(
                Subject.name == subject_data.name,
                Subject.id != subject_id
            )
            .first()
        )

        if existing_name:
            raise ValueError("Subject name already exists")

        subject.name = subject_data.name

    # update code
    if subject_data.code:

        existing_code = (
            db.query(Subject)
            .filter(
                Subject.code == subject_data.code,
                Subject.id != subject_id
            )
            .first()
        )

        if existing_code:
            raise ValueError("Subject code already exists")

        subject.code = subject_data.code

    # update semester
    if subject_data.semester is not None:

        if subject_data.semester < 1 or subject_data.semester > 8:
            raise ValueError("Semester must be between 1 and 8")

        subject.semester = subject_data.semester

    db.commit()
    db.refresh(subject)

    return subject


# ------------------------------------------------
# DELETE SUBJECT
# ------------------------------------------------
def delete_subject(
    db: Session,
    subject_id: int
):

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise ValueError("Subject not found")

    db.delete(subject)
    db.commit()

    return {
        "message": "Subject deleted successfully"
    }