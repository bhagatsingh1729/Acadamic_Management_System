from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.models import Student
from app.schemas.schema import StudentCreate, StudentUpdate
from app.core.security import hash_password

# Fix: removed unused imports StudentOut and StudentDelete
# Fix: renamed CreateStudent -> create_student to follow Python snake_case convention


def create_student(db: Session, student: StudentCreate) -> Student:
    # Fix: password is now hashed and stored instead of being silently ignored
    db_student = Student(
        usn=student.usn,
        name=student.name,
        email=student.email,
        age=student.age,
        branch=student.branch,
        hashed_password=hash_password(student.password),
    )
    # Fix: wrapped commit in try/except to handle duplicate USN or email gracefully
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

def create_students_bulk(db: Session, students: List[StudentCreate]) -> List[Student]:
    # 1. Create a list of Student database objects
    db_students = [
        Student(
            usn=s.usn,
            name=s.name,
            email=s.email,
            age=s.age,
            branch=s.branch,
            hashed_password=hash_password(s.password),
        )
        for s in students
    ]

    try:
        # 2. Add all objects to the session
        db.add_all(db_students)
        
        # 3. Commit once for the entire batch
        db.commit()
        
        # 4. Refresh objects to get generated IDs (if any)
        for s in db_students:
            db.refresh(s)
            
    except IntegrityError:
        # If even one student violates a constraint (like duplicate USN), 
        # the entire batch is rolled back to maintain data integrity.
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="One or more students have a duplicate USN or email. Batch insert failed.",
        )
        
    return db_students

def get_students(db: Session) -> list[Student]:
    return db.query(Student).all()


def get_student(db: Session, usn: str) -> Student:
    # Fix: now raises 404 if student not found instead of returning None
    student = db.query(Student).filter(Student.usn == usn).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with USN '{usn}' not found.")
    return student


def update_student(db: Session, usn: str, student: StudentUpdate) -> Student:
    db_student = db.query(Student).filter(Student.usn == usn).first()

    if not db_student:
        # Fix: added detail message to HTTPException
        raise HTTPException(status_code=404, detail=f"Student with USN '{usn}' not found.")

    # Fix: changed falsy checks (if student.x) to explicit None checks (if student.x is not None)
    # The old code would skip valid updates like age=0 or name="" since they are falsy
    if student.name is not None:
        db_student.name = student.name
    if student.email is not None:
        db_student.email = student.email
    if student.age is not None:
        db_student.age = student.age
    if student.branch is not None:
        db_student.branch = student.branch

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, usn: str) -> Student:
    db_student = db.query(Student).filter(Student.usn == usn).first()

    if not db_student:
        # Fix: added detail message to HTTPException
        raise HTTPException(status_code=404, detail=f"Student with USN '{usn}' not found.")

    db.delete(db_student)
    db.commit()
    return db_student
