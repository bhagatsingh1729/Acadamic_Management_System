from app.schemas.services_schemas.subject_schemas.student_subject_schemas import (
    EnrollmentRequest,
    EnrollmentResponse,
    StudentSchema,
    SubjectSchema,
)
from app.schemas.fundamental_schemas.student_subject_schema import (
    StudentSubjectCreate,
)
from app.crud.fundamental_crud.student_subject_crud import (
    enroll_student_to_subject,
)

from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException,status
from app.models.models import Student,Subject,StudentSubject,BranchSubject,Branch

def enroll_student_service(db: Session, data: EnrollmentRequest, enforced_branch_uid: str = None):
    # 1. Normalize and Fetch
    data.usn = data.usn.upper()
    data.code = data.code.upper()
    
    student = db.query(Student).filter(Student.usn == data.usn).first()
    subject = db.query(Subject).filter(Subject.code == data.code).first()
    
    if not student or not subject:
        raise HTTPException(status_code=404, detail="Student or Subject not found")

    # 2. Enforce Branch Logic
    # Verify the subject is valid for the student's branch
    mapping = db.query(BranchSubject).filter(
        BranchSubject.branch_id == student.branch_id,
        BranchSubject.subject_id == subject.id
    ).first()
    
    if not mapping:
        raise HTTPException(status_code=400, detail="Subject not available for this student's branch")

    # 3. Admin Enforcement
    if enforced_branch_uid:
        # Check if the student belongs to the admin's branch
        if student.branch.branch_uid != enforced_branch_uid:
            raise HTTPException(status_code=403, detail="You do not have access to this student's branch")

    # 4. Transactional Write
    try:
        enrollment = enroll_student_to_subject(db, student.id, subject.id)
        db.commit()
        db.refresh(enrollment)
        return EnrollmentResponse(
            student=StudentSchema.model_validate(student),
            subject=SubjectSchema.model_validate(subject),
            created_at=enrollment.created_at
        )   
    except HTTPException:
        db.rollback()
        raise # Rethrow the HTTPException so FastAPI catches it
    except Exception as e:
        db.rollback()
        # Handle unexpected system errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during enrollment."
        )
    
# =========================
# GET ALL ENROLLMENTS
# =========================
def get_all_enrollments_service(db: Session, enforced_branch_uid: Optional[str] = None):
    query = (
        db.query(StudentSubject)
        .join(Student, StudentSubject.student_id == Student.id)
        .join(Subject, StudentSubject.subject_id == Subject.id)
    )

    if enforced_branch_uid:
        query = query.join(Branch, Student.branch_id == Branch.id).filter(Branch.branch_uid == enforced_branch_uid)

    enrollments = query.all()
    
    # Map to schema
    return [
        EnrollmentResponse(
            student=StudentSchema.model_validate(e.student),
            subject=SubjectSchema.model_validate(e.subject),
            created_at=e.created_at
        ) for e in enrollments
    ]

# =========================
# GET ENROLLMENTS FOR SPECIFIC STUDENT
# =========================
def get_enrollments_for_student_service(db: Session, usn: str, enforced_branch_uid: Optional[str] = None):
    usn = usn.upper()
    student = db.query(Student).filter(Student.usn == usn).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if enforced_branch_uid and student.branch.branch_uid != enforced_branch_uid:
        raise HTTPException(status_code=403, detail="You do not have access to this student's branch")

    enrollments = db.query(StudentSubject).filter(StudentSubject.student_id == student.id).all()

    return [
        EnrollmentResponse(
            student=StudentSchema.model_validate(e.student),
            subject=SubjectSchema.model_validate(e.subject),
            created_at=e.created_at
        ) for e in enrollments
    ]

# =========================
# GET STUDENTS ENROLLED IN SUBJECT
# =========================
def get_students_enrolled_in_subject_service(db: Session, code: str, enforced_branch_uid: Optional[str] = None):
    code = code.upper()
    subject = db.query(Subject).filter(Subject.code == code).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if enforced_branch_uid:
        mapping = db.query(BranchSubject).join(Branch).filter(
            BranchSubject.subject_id == subject.id,
            Branch.branch_uid == enforced_branch_uid
        ).first()
        if not mapping:
            raise HTTPException(status_code=403, detail="You do not have access to this subject's branch")

    enrollments = db.query(StudentSubject).filter(StudentSubject.subject_id == subject.id).all()

    return [
        EnrollmentResponse(
            student=StudentSchema.model_validate(e.student),
            subject=SubjectSchema.model_validate(e.subject),
            created_at=e.created_at
        ) for e in enrollments
    ]

def delete_enrollment_service(db: Session, usn: str, code: str, enforced_branch_uid: Optional[str] = None):
    usn = usn.upper()
    code = code.upper()

    student = db.query(Student).filter(Student.usn == usn).first()
    subject = db.query(Subject).filter(Subject.code == code).first()

    if not student or not subject:
        raise HTTPException(status_code=404, detail="Student or Subject not found")

    # Admin branch enforcement
    if enforced_branch_uid:
        if student.branch.branch_uid != enforced_branch_uid:
            raise HTTPException(status_code=403, detail="You do not have access to this student's branch")

    enrollment = db.query(StudentSubject).filter(
        StudentSubject.student_id == student.id,
        StudentSubject.subject_id == subject.id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    try:
        db.delete(enrollment)
        db.commit()
        return {'message': 'Enrollment deleted successfully'}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the enrollment."
        )