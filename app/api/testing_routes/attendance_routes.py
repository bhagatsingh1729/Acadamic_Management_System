from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.attendance_schema import (
    AttendanceCreate,
    AttendanceResponse
)

from app.crud.fundamental_crud.attendance_crud import (
    create_attendance,
    generate_attendance_for_session,
    get_attendance_by_session,
    get_student_attendance,
    mark_attendance
)

router = APIRouter(
    prefix="/attendance",
    tags=["Attendance"]
)


@router.post("/", response_model=AttendanceResponse)
def create(data: AttendanceCreate, db: Session = Depends(get_db)):

    try:
        return create_attendance(db, data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate/{session_id}")
def generate(session_id: int, db: Session = Depends(get_db)):

    try:
        return generate_attendance_for_session(db, session_id)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}")
def session_attendance(session_id: int, db: Session = Depends(get_db)):

    return get_attendance_by_session(db, session_id)


@router.get("/student/{student_id}")
def student_attendance(student_id: int, db: Session = Depends(get_db)):

    return get_student_attendance(db, student_id)


@router.patch("/{attendance_id}")
def update(attendance_id: int, status: int, db: Session = Depends(get_db)):

    try:
        return mark_attendance(db, attendance_id, status)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))