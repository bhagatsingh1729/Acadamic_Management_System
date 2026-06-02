from app.database import get_db, SessionLocal  # Import your SessionLocal factory
from sqlalchemy.orm import Session
from fastapi import Depends
from app.models.models import Student,StudentSubject,Subject
from app.schemas.services_schemas.subject_schemas.student_subject_schemas import (
    EnrollmentResponse,
)
def test(db: Session = Depends(get_db)):
    query = (
        db.query(StudentSubject)
        .join(Student, StudentSubject.student_id == Student.id)
        .join(Subject, StudentSubject.subject_id == Subject.id)
        # Select the full objects and required fields
        .with_entities(
            Student.usn.label("usn"),
            Subject.code.label("subject_code"),
            StudentSubject.created_at.label("created_at") # Pulling the required timestamp
        )
    ).all()
    
    return [
        EnrollmentResponse(
            student={"usn": record.usn},               # Nested dictionary for student
            subject={"code": record.subject_code},     # Nested dictionary for subject
            created_at=record.created_at               # Passing required timestamp
        ) for record in query
    ]


if __name__ == "__main__":
    # 1. Manually instantiate a database session
    db = SessionLocal()
    
    try:
        # 2. Pass the session directly into the function
        students = test(db)
        
        # 3. Print your results
        for student in students:
            print(student)
        
    finally:
        # 4. Always close the session to prevent memory leaks
        db.close()
