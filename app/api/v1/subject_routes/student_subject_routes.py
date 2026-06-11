from app.services.subject_services.student_subject_services import (
    enroll_student_service,
    bulk_enroll_student_service,
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
from app.schemas.services_schemas.subject_schemas.subject_schemas import SubjectResponse
from app.schemas.response_schemas.person_responses import StudentResponse
from app.schemas.services_schemas.subject_schemas.student_subject_schemas import (
    EnrollmentRequest,
    EnrollmentResponse,
    BulkEnrollmentRequest,
    BulkEnrollmentResponse,
)
from app.schemas.response_schemas.API_Response import ApiResponse

from app.models.models import Admin, Branch, StudentSubject, Subject, BranchSubject
from fastapi import HTTPException,Depends,APIRouter,status

router = APIRouter(prefix="/enrollments",tags=["Enrollments"])

@router.post("",response_model=ApiResponse[EnrollmentResponse])
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

    result = enroll_student_service(db=db, data=data, enforced_branch_uid=enforced_branch_uid)
    return ApiResponse(success=True,message='student enrolled',data=result)

#this one is for bulk enrollment
@router.post("/bulk", response_model=ApiResponse[BulkEnrollmentResponse])
def bulk_enroll_students_route(
    data: BulkEnrollmentRequest, 
    db: Session = Depends(get_db), 
    current_user = Depends(require_roles('admin','super_admin'))
):
    """
    This endpoint is used by admin and super_admin to enroll multiple 
    students to subjects in a single request.
    """
    enforced_branch_uid = None
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid

    result = bulk_enroll_student_service(db=db, data=data, enforced_branch_uid=enforced_branch_uid)
    
    return ApiResponse(
        success=True,
        message=f"Bulk enrollment processed. Success: {result.successful}, Failed: {result.failed}",
        data=result
    )

@router.get("",response_model=ApiResponse[list[EnrollmentResponse]])
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

    result = get_all_enrollments_service(db=db, enforced_branch_uid=enforced_branch_uid)
    return ApiResponse(success=True,message='student enrollments',data=result)

@router.get("/student/{usn}", response_model=ApiResponse[list[SubjectResponse]])
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

    result = get_enrollments_for_student_service(db=db, usn=usn, enforced_branch_uid=enforced_branch_uid)
    return ApiResponse(success=True,message='students enrollments',data=result)

@router.get("/subject/{code}", response_model=ApiResponse[list[StudentResponse]])
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

    result = get_students_enrolled_in_subject_service(db=db, code=code, enforced_branch_uid=enforced_branch_uid)
    return ApiResponse(success=True,message='students enrolled in this subject',data=result)

@router.delete("/student/{usn}/subject/{code}", response_model=ApiResponse[None])
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

    delete_enrollment_service(db=db, usn=usn, code=code, enforced_branch_uid=enforced_branch_uid)
    return ApiResponse(success=True,message='enrollment deleted successfully',data=None)


    





