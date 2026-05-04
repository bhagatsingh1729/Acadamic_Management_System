from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.crud import CreateStudent, get_students, get_student, update_student, delete_student
from app.database import Base, engine, SessionLocal
from app.schema import StudentCreate, StudentOut, StudentUpdate, StudentDelete



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.post('/students', response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    return CreateStudent(db, student)

@router.get('/students', response_model=list[StudentOut])
def read_students(db: Session = Depends(get_db)):
    return get_students(db)

@router.get('/students/{usn}', response_model=StudentOut)
def read_student(usn: str, db: Session = Depends(get_db)):
    return get_student(db, usn)

@router.put('/students/{usn}', response_model=StudentOut)
def update_student_data(usn: str, student: StudentUpdate, db: Session = Depends(get_db)):
    return update_student(db, usn, student)

@router.delete('/students/{usn}', response_model=StudentOut)
def delete_student_data(usn: str, db: Session = Depends(get_db)):
    return delete_student(db, usn)

