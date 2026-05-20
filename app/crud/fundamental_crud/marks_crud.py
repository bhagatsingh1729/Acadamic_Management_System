# =========================================================
# marks_crud.py
# =========================================================

from sqlalchemy.orm import Session

from app.models.models import (
        Marks,
        Student,
        Exam,
        StudentSubject,
        Subject
)
from app.schemas.fundamental_schemas.marks_schema import MarksCreate


def create_marks(
    db: Session,
    data:MarksCreate
):

    # ---------------------------------------------------
    # validate student
    # ---------------------------------------------------

    student = (
        db.query(Student)
        .filter(Student.id == data.student_id)
        .first()
    )

    if not student:
        raise ValueError(
            "student not found"
        )

    # ---------------------------------------------------
    # validate exam
    # ---------------------------------------------------

    exam = (
        db.query(Exam)
        .filter(Exam.id == data.exam_id)
        .first()
    )

    if not exam:
        raise ValueError(
            "exam not found"
        )

    # ---------------------------------------------------
    # student semester validation
    # ---------------------------------------------------

    if student.semester != exam.semester:
        raise ValueError(
            "student semester does not match exam semester"
        )

    # ---------------------------------------------------
    # batch validation
    # ---------------------------------------------------

    if student.batch != exam.batch:
        raise ValueError(
            "student batch does not match exam batch"
        )

    # ---------------------------------------------------
    # subject enrollment validation
    # ---------------------------------------------------

    enrolled_subject = (
        db.query(StudentSubject)
        .filter(
            StudentSubject.student_id == student.id,
            StudentSubject.subject_id == exam.subject_id
        )
        .first()
    )

    if not enrolled_subject:
        raise ValueError(
            "student is not enrolled in this subject"
        )

    # ---------------------------------------------------
    # validate score
    # ---------------------------------------------------

    if data.score < 0:
        raise ValueError(
            "score cannot be negative"
        )

    if data.score > exam.max_marks:
        raise ValueError(
            "score exceeds max marks"
        )

    # ---------------------------------------------------
    # duplicate check
    # ---------------------------------------------------

    existing_marks = (
        db.query(Marks)
        .filter(
            Marks.student_id == data.student_id,
            Marks.exam_id == data.exam_id
        )
        .first()
    )

    if existing_marks:
        raise ValueError(
            "marks already exist"
        )

    # ---------------------------------------------------
    # create marks
    # ---------------------------------------------------

    marks = Marks(
        student_id=data.student_id,

        exam_id=data.exam_id,

        score=data.score
    )

    db.add(marks)

    db.commit()

    db.refresh(marks)

    return marks


def get_all_marks(
    db: Session
):

    marks = (
        db.query(Marks)
        .all()
    )

    return marks


def get_marks_by_id(
    db: Session,
    marks_id: int
):

    marks = (
        db.query(Marks)
        .filter(Marks.id == marks_id)
        .first()
    )

    if not marks:
        raise ValueError(
            "marks not found"
        )

    return marks


def get_marks_by_student(
    db: Session,
    student_id: int
):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise ValueError(
            "student not found"
        )

    marks = (
        db.query(Marks)
        .filter(Marks.student_id == student_id)
        .all()
    )

    return marks


def get_marks_by_exam(
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

    marks = (
        db.query(Marks)
        .filter(Marks.exam_id == exam_id)
        .all()
    )

    return marks


def update_marks(
    db: Session,
    marks_id: int,
    score: int
):

    marks = (
        db.query(Marks)
        .filter(Marks.id == marks_id)
        .first()
    )

    if not marks:
        raise ValueError(
            "marks not found"
        )

    exam = (
        db.query(Exam)
        .filter(Exam.id == marks.exam_id)
        .first()
    )

    if score < 0:
        raise ValueError(
            "score cannot be negative"
        )

    if score > exam.max_marks:
        raise ValueError(
            "score exceeds max marks"
        )

    marks.score = score

    db.commit()

    db.refresh(marks)

    return marks


def delete_marks(
    db: Session,
    marks_id: int
):

    marks = (
        db.query(Marks)
        .filter(Marks.id == marks_id)
        .first()
    )

    if not marks:
        raise ValueError(
            "marks not found"
        )

    db.delete(marks)

    db.commit()

    return {
        "message": "marks deleted successfully"
    }