from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.crud.crud import create_student, get_students, get_student, update_student, delete_student, create_students_bulk
from app.database import get_db  # Fix: get_db moved to database.py; removed unused Base and engine imports
from app.schemas.schema import StudentCreate, StudentOut, StudentUpdate

router = APIRouter()


@router.post("/students", response_model=StudentOut, status_code=201)
def create_student_route(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db, student)

@router.post("/student-bulk", response_model=list[StudentOut], status_code=201)
def create_students_bulk_route(students: List[StudentCreate], db: Session = Depends(get_db)):
    return create_students_bulk(db, students)

@router.get("/students", response_model=list[StudentOut])
def read_students(db: Session = Depends(get_db)):
    return get_students(db)


@router.get("/students/{usn}", response_model=StudentOut)
def read_student(usn: str, db: Session = Depends(get_db)):
    return get_student(db, usn)


@router.put("/students/{usn}", response_model=StudentOut)
def update_student_data(usn: str, student: StudentUpdate, db: Session = Depends(get_db)):
    return update_student(db, usn, student)


@router.delete("/students/{usn}", response_model=StudentOut)
def delete_student_data(usn: str, db: Session = Depends(get_db)):
    return delete_student(db, usn)

