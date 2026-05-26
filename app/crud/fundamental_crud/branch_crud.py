from sqlalchemy.orm import Session
from app.models.models import Branch, Student, Admin, User, StudentSubject, BranchSubject
from fastapi import HTTPException

from app.schemas.fundamental_schemas.branch_schema import (
    BranchCreate,
    BranchUpdate
)
from sqlalchemy.exc import SQLAlchemyError
from app.crud.fundamental_crud.student_crud import delete_student

from sqlalchemy.exc import SQLAlchemyError

def create_branch(db: Session, branch_data: BranchCreate):
    # 1. Check for existing branch
    existing_branch = db.query(Branch).filter(Branch.branch_uid == branch_data.branch_uid.upper()).first() 
    if existing_branch:
        raise HTTPException(status_code=409, detail="Branch already exists")
    
    # 2. Create the branch model instance
    # Tip: Use .model_dump() if using Pydantic V2 to map fields automatically
    # branch = Branch(**branch_data.model_dump())-> this menthod work
    branch = Branch(
        name = branch_data.name.upper(),
        branch_uid = branch_data.branch_uid.upper()
    )
    
    try:
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch
    except SQLAlchemyError as e:
        # Rollback is crucial when an error occurs during commit
        db.rollback()
        # Log the actual error 'e' internally, but return a clean error to the user
        raise HTTPException(status_code=500, detail="Database operation failed")


def get_all_branches(db: Session):

    return db.query(Branch).all()


def get_branch_by_id(db: Session, branch_id: int):

    return (
        db.query(Branch)
        .filter(Branch.id == branch_id)
        .first()
    )


def get_branch_by_uid(db: Session, branch_uid: str):

    return (
        db.query(Branch)
        .filter(Branch.branch_uid == branch_uid.upper())
        .first()
    )


def update_branch(
    db: Session,
    branch_id: int,
    branch_data: BranchUpdate
):

    branch = (
        db.query(Branch)
        .filter(Branch.id == branch_id)
        .first()
    )

    if not branch:
        return None

    update_data = branch_data.model_dump(exclude_unset=True)

    # enforcing uppercase to branch_uid
    if "branch_uid" in update_data:
        update_data["branch_uid"] = branch_data.branch_uid.upper()

    for key, value in update_data.items():
        setattr(branch, key, value)

    db.commit()
    db.refresh(branch)

    return branch


def delete_branch(db: Session, branch_id: int):
    try:
        # 1. Fetch data
        branch = db.query(Branch).filter(Branch.id == branch_id).first()
        if not branch: return None

        student_ids = [row[0] for row in db.query(Student.id).filter(Student.branch_id == branch_id).all()]
        
        # 2. Cleanup students
        if student_ids:
            db.query(StudentSubject).filter(StudentSubject.student_id.in_(student_ids)).delete(synchronize_session=False)

            # 3. Cleanup Users (Linked to Students)
            user_ids = [u[0] for u in db.query(Student.user_id).filter(Student.id.in_(student_ids)).all()]
            if user_ids:
                db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
            
            # 4. Cleanup Students
            db.query(Student).filter(Student.branch_id == branch_id).delete(synchronize_session=False)

        # 5. Cleanup Admin
        branch_admin = db.query(Admin).filter(Admin.branch_id == branch_id).first()
        if branch_admin:
            db.query(User).filter(User.id == branch_admin.user_id).delete(synchronize_session=False)
            db.delete(branch_admin)

        # delete branch_subject
        # 1. Correctly query the IDs of the BranchSubject records you want to delete
        branch_subjects = db.query(BranchSubject.id).filter(BranchSubject.branch_id == branch.id).all()
        branch_subject_ids = [bs[0] for bs in branch_subjects]

        # 2. Correctly delete them using a filter
        if branch_subject_ids:
            db.query(BranchSubject).filter(BranchSubject.id.in_(branch_subject_ids)).delete(synchronize_session=False)

        # 6. Delete Branch
        db.delete(branch)
        
        db.commit()
        return {'message': 'branch deleted'}
        
    except Exception as e:
        db.rollback()
        raise e



