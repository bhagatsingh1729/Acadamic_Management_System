from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app_v2.database import get_db

from app_v2.crud.student_crud import create_student,get_student,get_students,update_student
from app_v2.schemas.student_schema import StudentCreate,StudentRead,StudentUpdate,StudentOut

router_student = APIRouter()


@router_student.post("/create-student/{user_id}",response_model=StudentRead)
def create_student_route(student:StudentCreate,user_id:int,db:Session = Depends(get_db)):
    return create_student(db, student, user_id)


@router_student.get("/students",response_model=StudentRead)
def get_students_route(db:Session = Depends(get_db)):
    return get_students(db)

@router_student.get("/student/{usn}",response_model=StudentRead)
def get_student_route(usn:str,db:Session = Depends(get_db)):
    return get_student(db,usn)

@router_student.put("/student-update/{usn}",response_model=StudentRead)
def update_student_route(usn:str,student:StudentUpdate,db:Session = Depends(get_db)):
    return update_student(db=db,student=student,usn=usn)
