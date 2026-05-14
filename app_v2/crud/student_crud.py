from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app_v2.models.models import User,Student,Faculty,Admin
from app_v2.schemas.student_schema import StudentCreate, StudentRead, StudentUpdate, StudentOut
from app_v2.core.security import hash_password

def create_student(db:Session,student:StudentCreate,user_id:int)->StudentRead:
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found")
    if db_user.role != "student":
        raise HTTPException(status_code=400,detail="Associated user must have role 'student'")
    db_student = Student(
        usn=student.usn,
        branch=student.branch
    )   
    try:
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A student with this USN or email already exists.",
        )
    return db_student

def get_students(db:Session)->List[StudentRead]:
    db_std = db.query(Student).all()
    return db_std

def get_student(db:Session,usn:str)->StudentRead:
    db_std = db.query(Student).filter(Student.usn == usn).first()
    if not db_std:
        raise HTTPException(status_code=404,detail="student not found")
    return db_std

def update_student(db:Session,student:StudentUpdate,usn:str)->StudentRead:
    db_std = db.query(Student).filter(Student.usn == usn).first()
    if not db_std:
        raise HTTPException(status_code=404,detail='student not found')
    db.add(db_std)
    db.commit()
    db.refresh()

    return db_std
 