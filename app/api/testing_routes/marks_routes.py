# =========================================================
# marks_routes.py
# =========================================================

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.marks_schema import (
    MarksCreate,
    MarksResponse
)

from app.crud.fundamental_crud.marks_crud import (
    create_marks,
    get_all_marks,
    get_marks_by_id,
    get_marks_by_student,
    get_marks_by_exam,
    update_marks,
    delete_marks
)

router = APIRouter(
    prefix="/marks",
    tags=["Marks"]
)


@router.post(
    "/",
    response_model=MarksResponse
)
def create_new_marks(
    data: MarksCreate,
    db: Session = Depends(get_db)
):

    try:

        return create_marks(
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
    response_model=list[MarksResponse]
)
def get_marks(
    db: Session = Depends(get_db)
):

    return get_all_marks(db)


@router.get(
    "/{marks_id}",
    response_model=MarksResponse
)
def get_single_marks(
    marks_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_marks_by_id(
            db,
            marks_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/student/{student_id}",
    response_model=list[MarksResponse]
)
def get_student_marks(
    student_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_marks_by_student(
            db,
            student_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get(
    "/exam/{exam_id}",
    response_model=list[MarksResponse]
)
def get_exam_marks(
    exam_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_marks_by_exam(
            db,
            exam_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/{marks_id}"
)
def edit_marks(
    marks_id: int,
    score: int,
    db: Session = Depends(get_db)
):

    try:

        return update_marks(
            db,
            marks_id,
            score
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{marks_id}")
def remove_marks(
    marks_id: int,
    db: Session = Depends(get_db)
):

    try:

        return delete_marks(
            db,
            marks_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )