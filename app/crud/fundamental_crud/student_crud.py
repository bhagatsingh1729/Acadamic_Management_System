from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.models import (
    User,
    Student,
    Branch,
    StudentSubject
)


from app.schemas.fundamental_schemas.student_schema import StudentCreate, StudentUpdate


from app.core.security import hash_password


def create_student(db: Session, data: StudentCreate):

    existing_email = (
        db.query(User)
        .filter(User.email == data.email)
        .first()
    )

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="email already exists"
        )

    

    existing_usn = (
        db.query(Student)
        .filter(Student.usn == data.usn.upper())
        .first()
    )

    if existing_usn:
        raise HTTPException(
            status_code=400,
            detail="usn already exists"
        )

    #checking if branch exists
    branch_db = db.query(Branch).filter(Branch.id == data.branch_id).first()
    if not branch_db:
        raise HTTPException(
            status_code=404,
            detail="branch not found"
        )
    
    try:

        user = User(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),

            role="student",


            phone_no=data.phone_no,
            dob=data.dob,
            address=data.address
        )

        db.add(user)
        db.flush()

        student = Student(
            user_id=user.id,

            usn=data.usn.upper(),# let usn be uppercase so it would be easy to query and avoid duplicate usn because of case

            semester=data.semester,
            batch=data.batch,
            section=data.section.upper(),# Same reason here as well

            branch_id=data.branch_id
        )

        db.add(student)

        db.commit()
        db.refresh(student)

        return student

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def get_student_by_id(db: Session, student_id: int):

    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    return student


def get_student_by_usn(db: Session, usn: str):

    student = (
        db.query(Student)
        .filter(Student.usn == usn.upper())
        .first()
    )

    if not student:
        raise HTTPException(
            status_code=404,
            detail="student not found"
        )

    return student


def get_all_students(db: Session):

    return db.query(Student).limit(100).all()


def get_students_by_branch(db: Session, branch_id: int):

    return (
        db.query(Student)
        .filter(Student.branch_id == branch_id)
        .all()
    )


def get_students_by_semester(db: Session, semester: int):

    return (
        db.query(Student)
        .filter(Student.semester == semester)
        .limit(100)
        .all()
    )


def get_students_by_batch(db: Session, batch: str):

    return (
        db.query(Student)
        .filter(Student.batch == batch)
        .limit(100)
        .all()
    )


def get_students_by_section(db: Session, section: str):

    return (
        db.query(Student)
        .filter(Student.section == section.upper())
        .limit(100)
        .all()
    )


def get_students_by_cohort(
    db: Session,
    branch_id: int,
    semester: int,
    batch: str,
    section: str
):

    return (
        db.query(Student)
        .filter(
            Student.branch_id == branch_id,
            Student.semester == semester,
            Student.batch == batch,
            Student.section == section.upper()
        )
        .limit(100)
        .all()
    )


def update_student(db: Session, student_id: int, data: StudentUpdate):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="student not found")

    if data.branch_id:
        branch = db.query(Branch).filter(Branch.id == data.branch_id).first()
        if not branch:
            raise HTTPException(status_code=404, detail="branch not found")

    update_data = data.model_dump(exclude_unset=True)

    # Normalize casing
    for field in ["section", "usn", "batch"]:
        if field in update_data and update_data[field] is not None:
            update_data[field] = update_data[field].upper()

    # ─── Split fields between Student and User tables ─────────
    student_fields = {"semester", "batch", "section", "branch_id"}
    user_fields    = {"phone_no", "dob", "address"}

    for key, value in update_data.items():
        if key in student_fields:
            setattr(student, key, value)       # → updates student table
        elif key in user_fields and student.user:
            setattr(student.user, key, value)  # → updates user table

    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student_id: int):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="student not found")

    db.query(StudentSubject).filter(
        StudentSubject.student_id == student_id
    ).delete(synchronize_session=False)

    if student.user:
        db.delete(student.user)

    db.delete(student)
    db.commit()

    return {"message": "student deleted successfully"}