from sqlalchemy.orm import Session
from app.models import Student
from app.schema import StudentCreate,StudentOut,StudentUpdate,StudentDelete
from fastapi import HTTPException

def CreateStudent(db:Session,student:StudentCreate):
    db_student = Student(
        usn = student.usn,
        name = student.name,
        email = student.email,
        age = student.age,
        branch = student.branch
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student

def get_students(db:Session):
    return db.query(Student).all()

def get_student(db: Session, usn: str):
    return (
        db
        .query(Student)
        .filter(Student.usn == usn)
        .first()
    )

def update_student(db:Session,usn:str,student:StudentUpdate):
    db_student = db.query(Student).filter(Student.usn == usn).first()

    #check does the data exist
    if db_student:
        db_student.name = student.name if student.name else db_student.name
        db_student.email = student.email if student.email else db_student.email
        db_student.age = student.age if student.age else db_student.age
        db_student.branch = student.branch if student.branch else db_student.branch

        db.commit()
        db.refresh(db_student)
        return db_student
    raise HTTPException(status_code=404)

def delete_student(db:Session,usn:str):
    db_student = db.query(Student).filter(Student.usn == usn).first()
    #check if data exist
    if db_student:
        db.delete(db_student)
        db.commit()

        return db_student
    raise HTTPException(status_code=404)

