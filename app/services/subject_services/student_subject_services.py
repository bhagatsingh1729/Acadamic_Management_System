from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.models import Branch, BranchSubject, Student, StudentSubject, Subject
from app.schemas.fundamental_schemas.student_subject_schema import (
    StudentSubjectCreate,
)
from app.schemas.services_schemas.subject_schemas.student_subject_schemas import (
    EnrollmentRequest,
    EnrollmentResponse,
)
from app.crud.fundamental_crud.student_subject_crud import (
    enroll_student_to_subject,
)
from app.schemas.response_schemas.person_responses import StudentResponse
# =========================
# ENROLL STUDENT
# =========================
def enroll_student_service(db: Session, data: EnrollmentRequest, enforced_branch_uid: str = None):
    # 1. Normalize Input Data
    data.usn = data.usn.upper()
    data.code = data.code.upper()
    
    # Eagerly load branch to optimize the admin enforcement check later
    student = db.query(Student).options(joinedload(Student.branch)).filter(Student.usn == data.usn).first()
    subject = db.query(Subject).filter(Subject.code == data.code).first()
    
    if not student or not subject:
        raise HTTPException(status_code=404, detail="Student or Subject not found")

    # 2. Enforce Branch Logic (Check if branch offers this course)
    mapping = db.query(BranchSubject).filter(
        BranchSubject.branch_id == student.branch_id,
        BranchSubject.subject_id == subject.id
    ).first()
    
    if not mapping:
        raise HTTPException(status_code=400, detail="Subject not available for this student's branch")

    # 3. Admin Scope Enforcement 
    if enforced_branch_uid:
        if student.branch.branch_uid != enforced_branch_uid:
            raise HTTPException(status_code=403, detail="You do not have access to this student's branch")

    # 4. Transactional Write
    try:
        enrollment = enroll_student_to_subject(db, student.id, subject.id)
        db.commit()
        db.refresh(enrollment)
        
        return EnrollmentResponse(
            usn=student.usn,
            subject=subject
        )   
    except HTTPException:
        db.rollback()
        raise 
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during enrollment."
        )
    
# =========================
# GET ALL ENROLLMENTS
# =========================
def get_all_enrollments_service(db: Session, enforced_branch_uid: Optional[str] = None):
    query = db.query(StudentSubject)

    # If branch-specific admin, apply JOIN filters to scope data boundaries safely
    if enforced_branch_uid:
        query = (
            query.join(Student, StudentSubject.student_id == Student.id)
            .join(Branch, Student.branch_id == Branch.id)
            .filter(Branch.branch_uid == enforced_branch_uid)
        )

    # FIXED: Added joinedload options so the loop transforms rows instantly without N+1 db hits
    enrollments = query.options(
        joinedload(StudentSubject.student),
        joinedload(StudentSubject.subject)
    ).all()
    
    return [
        EnrollmentResponse(
            usn=e.student.usn,
            subject=e.subject
        ) for e in enrollments
    ]


# =========================
# GET ENROLLMENTS FOR SPECIFIC STUDENT
# =========================
def get_enrollments_for_student_service(db: Session, usn: str, enforced_branch_uid: Optional[str] = None):
    usn = usn.upper()
    
    student = db.query(Student).options(joinedload(Student.branch)).filter(Student.usn == usn).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if enforced_branch_uid and student.branch.branch_uid != enforced_branch_uid:
        raise HTTPException(status_code=403, detail="You do not have access to this student's branch")

    enrollments = (
        db.query(StudentSubject)
        .filter(StudentSubject.student_id == student.id)
        .options(joinedload(StudentSubject.subject))  # FIX: Removed unneeded student load
        .all()
    )

    return [e.subject for e in enrollments]


# =========================
# GET STUDENTS ENROLLED IN SUBJECT
# =========================
def get_students_enrolled_in_subject_service(db: Session, code: str, enforced_branch_uid: Optional[str] = None):
    code = code.upper()
    subject = db.query(Subject).filter(Subject.code == code).first()
    
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # CHAINED JOINEDLOAD: Fetches Student, Student's User, and Student's Branch in 1 single query
    query = (
        db.query(StudentSubject)
        .filter(StudentSubject.subject_id == subject.id)
        .options(
            joinedload(StudentSubject.student).joinedload(Student.user),
            joinedload(StudentSubject.student).joinedload(Student.branch)
        )
    )

    if enforced_branch_uid:
        query = query.join(Student).join(Branch).filter(Branch.branch_uid == enforced_branch_uid)

    enrollments = query.all()

    # Explicitly construct the response schema to map the nested branch_uid directly
    return [
        StudentResponse(
            id=e.student.id,
            user_id=e.student.user_id,
            usn=e.student.usn,
            semester=e.student.semester,
            batch=e.student.batch,
            section=e.student.section,
            branch_id=e.student.branch_id,
            branch_uid=e.student.branch.branch_uid,  # <-- Map the nested data here
            user=e.student.user                       # <-- Pre-loaded safely
        ) for e in enrollments
    ]

# =========================
# DELETE ENROLLMENT
# =========================
def delete_enrollment_service(db: Session, usn: str, code: str, enforced_branch_uid: Optional[str] = None):
    usn = usn.upper()
    code = code.upper()

    # Pre-loaded branch to save a lazy-loading query during compliance check
    student = db.query(Student).options(joinedload(Student.branch)).filter(Student.usn == usn).first()
    subject = db.query(Subject).filter(Subject.code == code).first()

    if not student or not subject:
        raise HTTPException(status_code=404, detail="Student or Subject not found")

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
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the enrollment."
        )