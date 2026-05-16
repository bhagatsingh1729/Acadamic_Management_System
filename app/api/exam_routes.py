# =========================================================
# exam_routes.py
# =========================================================

from fastapi import APIRouter,Depends, HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.exam_schema import (
    ExamCreate,
    ExamResponse
)

from app.crud.exam_crud import (
    create_exam,
    get_all_exams,
    get_exam_by_id,
    get_exams_by_subject,
    delete_exam
)

router = APIRouter(
    prefix="/exams",
    tags=["Exam"]
)


@router.post(
    "/",
    response_model=ExamResponse
)
def create_new_exam(
    data: ExamCreate,
    db: Session = Depends(get_db)
):

    try:

        return create_exam(
            db,
            data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[ExamResponse]
)
def get_exams(
    db: Session = Depends(get_db)
):

    return get_all_exams(db)


@router.get(
    "/{exam_id}",
    response_model=ExamResponse
)
def get_single_exam(
    exam_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_exam_by_id(
            db,
            exam_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/subject/{subject_id}",
    response_model=list[ExamResponse]
)
def get_subject_exams(
    subject_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_exams_by_subject(
            db,
            subject_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete("/{exam_id}")
def remove_exam(
    exam_id: int,
    db: Session = Depends(get_db)
):

    try:

        return delete_exam(
            db,
            exam_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )