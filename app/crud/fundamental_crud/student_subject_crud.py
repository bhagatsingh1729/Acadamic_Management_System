# =========================================================
# student_subject_crud.py
# =========================================================

from sqlalchemy.orm import Session

from app.schemas.fundamental_schemas.student_subject_schema import StudentSubjectCreate


from app.models.models import (
    Student,
    Subject,
    StudentSubject,
    BranchSubject
)


def enroll_student_to_subject(
    db: Session,
    student_id: int,
    subject_id: int
):

    # ---------------------------------------------------
    # check student
    # ---------------------------------------------------

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise ValueError(
            "student not found"
        )

    # ---------------------------------------------------
    # check subject
    # ---------------------------------------------------

    subject = (
        db.query(Subject)
        .filter(Subject.id == subject_id)
        .first()
    )

    if not subject:
        raise ValueError(
            "subject not found"
        )

    # ---------------------------------------------------
    # subject must belong to student's branch
    # ---------------------------------------------------

    branch_subject = (
        db.query(BranchSubject)
        .filter(
            BranchSubject.branch_id == student.branch_id,
            BranchSubject.subject_id == subject_id
        )
        .first()
    )

    if not branch_subject:
        raise ValueError(
            "subject does not belong to student's branch"
        )

    # ---------------------------------------------------
    # semester validation
    # ---------------------------------------------------

    if student.semester != subject.semester:
        raise ValueError(
            "student semester does not match subject semester"
        )

    # ---------------------------------------------------
    # duplicate enrollment check
    # ---------------------------------------------------

    existing_enrollment = (
        db.query(StudentSubject)
        .filter(
            StudentSubject.student_id == student_id,
            StudentSubject.subject_id == subject_id
        )
        .first()
    )

    if existing_enrollment:
        raise ValueError(
            "student already enrolled to subject"
        )

    # ---------------------------------------------------
    # create enrollment
    # ---------------------------------------------------

    enrollment = StudentSubject(
        student_id=student_id,
        subject_id=subject_id
    )

    db.add(enrollment)

    db.commit()

    db.refresh(enrollment)

    return enrollment


def get_all_student_subjects(
    db: Session
):

    enrollments = (
        db.query(StudentSubject)
        .all()
    )

    return enrollments


def get_subjects_of_student(
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

    enrollments = (
        db.query(StudentSubject)
        .filter(StudentSubject.student_id == student_id)
        .all()
    )

    return enrollments


def get_students_of_subject(
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

    enrollments = (
        db.query(StudentSubject)
        .filter(StudentSubject.subject_id == subject_id)
        .all()
    )

    return enrollments


def remove_student_enrollment(
    db: Session,
    enrollment_id: int
):

    enrollment = (
        db.query(StudentSubject)
        .filter(StudentSubject.id == enrollment_id)
        .first()
    )

    if not enrollment:
        raise ValueError(
            "enrollment not found"
        )

    db.delete(enrollment)

    db.commit()

    return {
        "message": "student enrollment removed successfully"
    }