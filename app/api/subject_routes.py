from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.subject import (
    SubjectCreate,
    SubjectUpdate,
    SubjectResponse
)

from app.crud.subject_crud import (
    create_subject,
    get_all_subjects,
    get_subject_by_id,
    get_subject_by_code,
    get_subjects_by_semester,
    update_subject,
    delete_subject
)

router_subject = APIRouter(
    prefix="/subjects",
    tags=["Subjects"]
)


# ------------------------------------------------
# CREATE SUBJECT
# ------------------------------------------------
@router_subject.post("/", response_model=SubjectResponse)
def create_subject_route(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db)
):

    try:
        return create_subject(
            db,
            subject_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ------------------------------------------------
# GET ALL SUBJECTS
# ------------------------------------------------
@router_subject.get("/", response_model=list[SubjectResponse])
def get_all_subjects_route(
    db: Session = Depends(get_db)
):

    return get_all_subjects(db)


# ------------------------------------------------
# GET SUBJECT BY ID
# ------------------------------------------------
@router_subject.get("/{subject_id}", response_model=SubjectResponse)
def get_subject_route(
    subject_id: int,
    db: Session = Depends(get_db)
):

    try:
        return get_subject_by_id(
            db,
            subject_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ------------------------------------------------
# GET SUBJECT BY CODE
# ------------------------------------------------
@router_subject.get("/code/{subject_code}", response_model=SubjectResponse)
def get_subject_by_code_route(
    subject_code: str,
    db: Session = Depends(get_db)
):

    try:
        return get_subject_by_code(
            db,
            subject_code
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ------------------------------------------------
# GET SUBJECTS BY SEMESTER
# ------------------------------------------------
@router_subject.get("/semester/{semester}", response_model=list[SubjectResponse])
def get_subjects_by_semester_route(
    semester: int,
    db: Session = Depends(get_db)
):

    try:
        return get_subjects_by_semester(
            db,
            semester
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ------------------------------------------------
# UPDATE SUBJECT
# ------------------------------------------------
@router_subject.put("/{subject_id}", response_model=SubjectResponse)
def update_subject_route(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db)
):

    try:
        return update_subject(
            db,
            subject_id,
            subject_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ------------------------------------------------
# DELETE SUBJECT
# ------------------------------------------------
@router_subject.delete("/{subject_id}")
def delete_subject_route(
    subject_id: int,
    db: Session = Depends(get_db)
):

    try:
        return delete_subject(
            db,
            subject_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )