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

    return db.query(Student).all()


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
        .all()
    )


def get_students_by_batch(db: Session, batch: str):

    return (
        db.query(Student)
        .filter(Student.batch == batch)
        .all()
    )


def get_students_by_section(db: Session, section: str):

    return (
        db.query(Student)
        .filter(Student.section == section.upper())
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
        .all()
    )


def update_student(
    db: Session,
    student_id: int,
    data: StudentUpdate
):

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

    if data.branch_id:

        branch = (
            db.query(Branch)
            .filter(Branch.id == data.branch_id)
            .first()
        )

        if not branch:
            raise HTTPException(
                status_code=404,
                detail="branch not found"
            )
    """
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(student, key, value)
    """
    # to make sure section and usn is uppercase
    update_data = data.model_dump(exclude_unset=True)

    # Force uppercase for specific fields if they exist in the update
    if 'section' in update_data:
        update_data['section'] = update_data['section'].upper()
    if 'usn' in update_data:
        update_data['usn'] = update_data['usn'].upper()

    for key, value in update_data.items():
        setattr(student, key, value)
        
    db.commit()
    db.refresh(student)

    return student


def delete_student(db: Session, student_id: int):

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

    # Deleting the student enrollment related data
    db.query(StudentSubject).filter(StudentSubject.student_id == student_id).delete(synchronize_session=False)
    
    if student.user:
        user_to_delete = student.user
        db.delete(user_to_delete)#adding this line so that when a student is getting deleted, their associated user record is also deleted


    db.delete(student)
    
    db.commit()



    return {
        "message": "student deleted successfully"
    }