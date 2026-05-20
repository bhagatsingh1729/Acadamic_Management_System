# =========================================================
# student_subject_routes.py
# =========================================================

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.student_subject_schema import (
    StudentSubjectCreate,
    StudentSubjectResponse
)

from app.crud.fundamental_crud.student_subject_crud import (
    enroll_student_to_subject,
    get_all_student_subjects,
    get_subjects_of_student,
    get_students_of_subject,
    remove_student_enrollment
)

router = APIRouter(
    prefix="/student-subjects",
    tags=["Student Subject Enrollment"]
)


@router.post(
    "/",
    response_model=StudentSubjectResponse
)
def enroll_student(
    data: StudentSubjectCreate,
    db: Session = Depends(get_db)
):

    try:

        return enroll_student_to_subject(
            db=db,
            student_id=data.student_id,
            subject_id=data.subject_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[StudentSubjectResponse]
)
def get_all_enrollments(
    db: Session = Depends(get_db)
):

    return get_all_student_subjects(db)


@router.get(
    "/student/{student_id}",
    response_model=list[StudentSubjectResponse]
)
def get_student_subjects(
    student_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_subjects_of_student(
            db,
            student_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/subject/{subject_id}",
    response_model=list[StudentSubjectResponse]
)
def get_subject_students(
    subject_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_students_of_subject(
            db,
            subject_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete("/{enrollment_id}")
def delete_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_db)
):

    try:

        return remove_student_enrollment(
            db,
            enrollment_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )