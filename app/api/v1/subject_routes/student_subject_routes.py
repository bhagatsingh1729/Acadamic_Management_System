from app.services.subject_services.student_subject_services import (
    enroll_student_service,
    get_all_enrollments_service,
    get_enrollments_for_student_service,
    get_students_enrolled_in_subject_service,
    delete_enrollment_service,
)
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.dependencies import (
    require_roles,
)

from app.schemas.services_schemas.subject_schemas.student_subject_schemas import (
    EnrollmentRequest,
    EnrollmentResponse,
)
from app.models.models import Admin, Branch, StudentSubject, Subject, BranchSubject
from fastapi import HTTPException,Depends,APIRouter,status

router = APIRouter(prefix="/enrollments",tags=["Enrollments"])

@router.post("",response_model=EnrollmentResponse)
def enroll_student_route(data:EnrollmentRequest,db:Session=Depends(get_db),current_user=Depends(require_roles('admin','super_admin'))):
    """
    this endpoint is used by admin and 
    super_admin to enroll student to a subject.
    """

    # Enforce branch restriction for admins
    enforced_branch_uid = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid  # ← admin's own branch_uid

    return enroll_student_service(db=db, data=data, enforced_branch_uid=enforced_branch_uid)

@router.get("",response_model=list[EnrollmentResponse])
def get_all_enrollments_route(db:Session=Depends(get_db),current_user=Depends(require_roles('admin','super_admin','faculty','hod'))):
    """
    this endpoint helps in getting all the enrollment
    list of students.
    """
     
    # Enforce branch restriction for admins
    enforced_branch_uid = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid  # ← admin's own branch_uid

    return get_all_enrollments_service(db=db, enforced_branch_uid=enforced_branch_uid)

@router.get("/student/{usn}",response_model=list[EnrollmentResponse])
def get_enrollments_for_student_route(usn:str,db:Session=Depends(get_db),current_user=Depends(require_roles('admin','super_admin','faculty','hod'))):
    """
    get enrollments of a student based
    on the staudent's usn
    """
    # Enforce branch restriction for admins
    enforced_branch_uid = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid  # ← admin's own branch_uid

    return get_enrollments_for_student_service(db=db, usn=usn, enforced_branch_uid=enforced_branch_uid)

@router.get("/subject/{code}",response_model=list[EnrollmentResponse])
def get_students_enrolled_in_subject_route(code:str,db:Session=Depends(get_db),current_user=Depends(require_roles('admin','super_admin','faculty','hod'))):
    """
    get enrollments for a specific subject
    based on the subject code
    """
    # Enforce branch restriction for admins
    enforced_branch_uid = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid  # ← admin's own branch_uid

    return get_students_enrolled_in_subject_service(db=db, code=code, enforced_branch_uid=enforced_branch_uid)

@router.delete("/student/{usn}/subject/{code}", response_model=dict)
def delete_enrollment_route(usn:str,code:str,db:Session=Depends(get_db),current_user=Depends(require_roles('admin','super_admin'))):
    """
    Endpoint to delete an enrollment based on
    usn and subject code
    """
    # Enforce branch restriction for admins
    enforced_branch_uid = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid  # ← admin's own branch_uid

    return delete_enrollment_service(db=db, usn=usn, code=code, enforced_branch_uid=enforced_branch_uid)


    





