from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app_v2.database import get_db

from app_v2.schemas.user_schema import StudentCreate, StudentRead
from app_v2.crud.user_crud import create_student

router_student = APIRouter()



@router_student.post("/create-student", response_model=StudentRead)
def create_student_route(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db, student)

