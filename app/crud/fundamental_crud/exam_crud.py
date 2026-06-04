# =========================================================
# exam_crud.py
# =========================================================

from sqlalchemy.orm import Session
from app.schemas.fundamental_schemas.exam_schema import ExamCreate
from app.models.models import Exam, Subject, Student
from fastapi import HTTPException

VALID_EXAM_TYPES = [
    "IA1",
    "IA2",
    "MID_SEM",
    "END_SEM"
]


def create_exam(
    db: Session,
    data:ExamCreate
):

    # ---------------------------------------------------
    # validate exam type
    # ---------------------------------------------------

    if data.type not in VALID_EXAM_TYPES:
        raise ValueError(
            "invalid exam type"
        )

    # ---------------------------------------------------
    # validate subject
    # ---------------------------------------------------

    subject = (
        db.query(Subject)
        .filter(Subject.id == data.subject_id)
        .first()
    )

    if not subject:
        raise ValueError(
            "subject not found"
        )

    # ---------------------------------------------------
    # semester validation
    # ---------------------------------------------------

    if data.semester != subject.semester:
        raise ValueError(
            "exam semester must match subject semester"
        )

    # ---------------------------------------------------
    # max marks validation
    # ---------------------------------------------------

    if data.max_marks <= 0:
        raise ValueError(
            "max_marks must be greater than 0"
        )

    # ---------------------------------------------------
    # students must exist
    # ---------------------------------------------------

    students_exist = (
        db.query(Student)
        .filter(
            Student.batch == data.batch,
            Student.semester == data.semester
        )
        .first()
    )

    if not students_exist:
        raise ValueError(
            "no students found for this batch and semester"
        )

    # ---------------------------------------------------
    # duplicate exam check
    # ---------------------------------------------------

    existing_exam = (
        db.query(Exam)
        .filter(
            Exam.type == data.type,
            Exam.subject_id == data.subject_id,
            Exam.batch == data.batch,
            Exam.semester == data.semester
        )
        .first()
    )

    if existing_exam:
        raise ValueError(
            "exam already exists"
        )

    # ---------------------------------------------------
    # create exam
    # ---------------------------------------------------

    exam = Exam(
        type=data.type,

        subject_id=data.subject_id,

        max_marks=data.max_marks,

        semester=data.semester,

        batch=data.batch,

        date=data.date
    )

    db.add(exam)

    #db.commit()

    #db.refresh(exam)

    return exam


def get_all_exams(
    db: Session
):

    exams = (
        db.query(Exam)
        .all()
    )

    return exams


def get_exam_by_id(
    db: Session,
    exam_id: int
):

    exam = (
        db.query(Exam)
        .filter(Exam.id == exam_id)
        .first()
    )

    if not exam:
        raise ValueError(
            "exam not found"
        )

    return exam


def get_exams_by_subject(
    db: Session,
    subject_id: int
):

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise ValueError(
            "subject not found"
        )

    exams = (
        db.query(Exam)
        .filter(Exam.subject_id == subject_id)
        .all()
    )

    return exams


def delete_exam(
    db: Session,
    exam_id: int
):

    exam = (
        db.query(Exam)
        .filter(Exam.id == exam_id)
        .first()
    )

    if not exam:
        raise HTTPException(
            status_code=404,
            detail="exam not found"
        )

    db.delete(exam)

    db.commit()

    return {
        "message": "exam deleted successfully"
    }