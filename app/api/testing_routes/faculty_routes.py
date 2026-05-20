from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.faculty_schema import (
    FacultyCreate,
    FacultyUpdate
)

from app.crud.fundamental_crud.faculty_crud import (
    create_faculty,
    get_all_faculty,
    get_faculty_by_id,
    update_faculty,
    delete_faculty
)


router = APIRouter(
    prefix="/faculty",
    tags=["Faculty"]
)


# =========================
# CREATE FACULTY
# =========================
@router.post("/")
def create_faculty_route(
    faculty_data: FacultyCreate,
    db: Session = Depends(get_db)
):

    return create_faculty(db, faculty_data)


# =========================
# GET ALL FACULTY
# =========================
@router.get("/")
def get_all_faculty_route(
    db: Session = Depends(get_db)
):

    return get_all_faculty(db)


# =========================
# GET FACULTY BY ID
# =========================
@router.get("/{faculty_id}")
def get_faculty_by_id_route(
    faculty_id: int,
    db: Session = Depends(get_db)
):

    return get_faculty_by_id(db, faculty_id)


# =========================
# UPDATE FACULTY
# =========================
@router.put("/{faculty_id}")
def update_faculty_route(
    faculty_id: int,
    faculty_data: FacultyUpdate,
    db: Session = Depends(get_db)
):

    return update_faculty(
        db,
        faculty_id,
        faculty_data
    )


# =========================
# DELETE FACULTY
# =========================
@router.delete("/{faculty_id}")
def delete_faculty_route(
    faculty_id: int,
    db: Session = Depends(get_db)
):

    return delete_faculty(db, faculty_id)