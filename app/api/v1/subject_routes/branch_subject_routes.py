from app.services.subject_services.branch_subject_services import (
    assign_subject_to_branch_service,
    get_all_branch_subjects_service,
    delete_branch_subject_service,
    get_subjects_of_branch_service,
)
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.dependencies import (
    require_roles,
)

from app.schemas.services_schemas.subject_schemas.branch_subject_schemas import (
    BranchSubjectCreateRequest,
    BranchSubjectUpdateRequest,
    MappingResponse,
    BranchSubjectFacultyResponse,
)
from app.schemas.response_schemas.API_Response import ApiResponse

from app.models.models import Admin, Branch, Subject, BranchSubject
from app.models.models import FacultySubject,Faculty,BranchSubject,User,Subject,Department
from fastapi import HTTPException,Depends,APIRouter

router = APIRouter(prefix="/branch-subjects",tags=["Branch-Subject Mapping"])

# =============================================================
# POST /branch-subjects — Assign subject to branch
# admin (own branch only) | super_admin
# =============================================================
@router.post("", response_model=ApiResponse[MappingResponse])
def assign_subject(
    data: BranchSubjectCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    enforced_branch_uid = None

    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid  

    result = assign_subject_to_branch_service(
        data=data,
        db=db,
        enforced_branch_uid=enforced_branch_uid
    )
    return ApiResponse(success=True,message='successfully assigned mapped subject to branch',data=result)


# =============================================================
# GET /branch-subjects — List all mappings
# admin | super_admin | faculty | hod
# =============================================================
@router.get("", response_model=ApiResponse[list[MappingResponse]])
def get_all_branch_subjects(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty", "hod"))
):
    result = get_all_branch_subjects_service(db=db)
    return ApiResponse(success=True,message='list of subjects of all branches',data=result)


# =============================================================
# GET /branch-subjects/branch/{branch_uid} — Subjects of a branch
# admin (own branch only) | super_admin | faculty | hod
# =============================================================
@router.get("/branch/{branch_uid}", response_model=ApiResponse[list[MappingResponse]])
def get_subjects_of_branch(
    branch_uid: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty", "hod"))
):
    # Admin can only view their own branch
    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        if admin.branch.branch_uid.upper() != branch_uid.upper():
            raise HTTPException(
                status_code=403,
                detail="You can only view subjects for your own branch"
            )

    result = get_subjects_of_branch_service(branch_uid=branch_uid, db=db)
    return ApiResponse(success=True,message='list if subjects of a branch',data=result)

@router.get("/faculties",response_model=ApiResponse[list[BranchSubjectFacultyResponse]])
def get_branch_subject_faculties_route(
    db: Session = Depends(get_db), 
    current_user = Depends(require_roles('admin'))
):
    # We anchor the query starting from FacultySubject
    query = (
        db.query(
            User.name.label("faculty_name"),
            Faculty.employee_id.label("employee_id"),    # Added employee_id
            Department.name.label("dept_name"),          # Added dept_name
            Subject.name.label("subject_name"),
            Subject.code.label("subject_code")
        )
        .select_from(FacultySubject)
        .join(Faculty, Faculty.id == FacultySubject.faculty_id)
        .join(User, User.id == Faculty.user_id)
        .join(Department, Department.id == Faculty.dept_id) # New Join for Department
        .join(Subject, Subject.id == FacultySubject.subject_id)
        .join(BranchSubject, BranchSubject.subject_id == Subject.id)
        .filter(BranchSubject.branch_id == current_user.admin.branch_id)
        .all()
    )

    if not query:
        raise HTTPException(status_code=404, detail="No faculties found for this branch")

    result = [row._asdict() for row in query]
    return ApiResponse(success=True,message='faculties who teach subjects to specific branches',data=result)

# =============================================================
# DELETE /branch-subjects/branch/{branch_uid}/subject/{code}
# admin (own branch only) | super_admin
# =============================================================
@router.delete("/branch/{branch_uid}/subject/{code}",response_model=ApiResponse[None])
def delete_branch_subject(
    branch_uid: str,
    code: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    enforced_branch_uid = None

    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid

    delete_branch_subject_service(
        branch_uid=branch_uid,
        subject_code=code,
        db=db,
        enforced_branch_uid=enforced_branch_uid
    )
    return ApiResponse(success=True,message='deleted mapping successfully',data=None)