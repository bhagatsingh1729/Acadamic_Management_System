from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.student_schema import (
    StudentCreate,
    StudentUpdate
)


from app.crud.fundamental_crud.student_crud import (
    create_student,
    get_student_by_id,
    get_student_by_usn,
    get_all_students,
    get_students_by_branch,
    get_students_by_semester,
    get_students_by_batch,
    get_students_by_section,
    get_students_by_cohort,
    update_student,
    delete_student
)


router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.post("/")
def create_student_route(
    data: StudentCreate,
    db: Session = Depends(get_db)
):
    return create_student(db, data)


@router.get("/")
def get_all_students_route(
    db: Session = Depends(get_db)
):
    return get_all_students(db)


@router.get("/{student_id}")
def get_student_route(
    student_id: int,
    db: Session = Depends(get_db)
):
    return get_student_by_id(db, student_id)


@router.get("/usn/{usn}")
def get_student_by_usn_route(
    usn: str,
    db: Session = Depends(get_db)
):
    return get_student_by_usn(db, usn)


@router.get("/branch/{branch_id}")
def get_students_by_branch_route(
    branch_id: int,
    db: Session = Depends(get_db)
):
    return get_students_by_branch(db, branch_id)


@router.get("/semester/{semester}")
def get_students_by_semester_route(
    semester: int,
    db: Session = Depends(get_db)
):
    return get_students_by_semester(db, semester)


@router.get("/batch/{batch}")
def get_students_by_batch_route(
    batch: str,
    db: Session = Depends(get_db)
):
    return get_students_by_batch(db, batch)


@router.get("/section/{section}")
def get_students_by_section_route(
    section: str,
    db: Session = Depends(get_db)
):
    return get_students_by_section(db, section)


@router.get("/cohort/filter")
def get_students_by_cohort_route(
    branch_id: int,
    semester: int,
    batch: str,
    section: str,
    db: Session = Depends(get_db)
):
    return get_students_by_cohort(
        db,
        branch_id,
        semester,
        batch,
        section
    )


@router.put("/{student_id}")
def update_student_route(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db)
):
    return update_student(
        db,
        student_id,
        data
    )


@router.delete("/{student_id}")
def delete_student_route(
    student_id: int,
    db: Session = Depends(get_db)
):
    return delete_student(db, student_id)