from app.services.subject_services.branch_subject_services import (
    assign_subject_to_branch_service,
    get_all_branch_subjects_service,
    delete_branch_subject_service,
    get_subjects_of_branch_service,
)
from app.database import get_db
from sqlalchemy.orm import Session
from app.core.dependencies import (
    require_admin,
    require_super_admin,
    require_roles,
)

from app.schemas.services_schemas.subject_schemas.branch_subject_schemas import (
    BranchSubjectCreateRequest,
    BranchSubjectUpdateRequest,
    Branch_Subjects_response,
    MappingResponse,
)
from app.models.models import Admin, Branch, Subject, BranchSubject
from fastapi import HTTPException,Depends,APIRouter

router = APIRouter(prefix="/branch-subjects",tags=["Branch-Subject Mapping"])

# =============================================================
# POST /branch-subjects — Assign subject to branch
# admin (own branch only) | super_admin
# =============================================================
@router.post("", response_model=dict)
def assign_subject(
    data: BranchSubjectCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin"))
):
    # Kepping it none so if the current user is not admin we can pass none
    enforced_branch_uid = None

    if current_user.role == "admin":
        admin: Admin = db.query(Admin).filter(# query in admin table to retrieve branch_uid,so that we can assign that to enforced_branch_id
            Admin.user_id == current_user.id
        ).first()
        enforced_branch_uid = admin.branch.branch_uid  # ← admin's own branch_uid

    return assign_subject_to_branch_service(
        data=data,
        db=db,
        enforced_branch_uid=enforced_branch_uid
    )


# =============================================================
# GET /branch-subjects — List all mappings
# admin | super_admin | faculty | hod
# =============================================================
@router.get("", response_model=list[MappingResponse])
def get_all_branch_subjects(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "faculty", "hod"))
):
    return get_all_branch_subjects_service(db=db)


# =============================================================
# GET /branch-subjects/branch/{branch_uid} — Subjects of a branch
# admin (own branch only) | super_admin | faculty | hod
# =============================================================
@router.get("/branch/{branch_uid}", response_model=list[MappingResponse])
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

    return get_subjects_of_branch_service(branch_uid=branch_uid, db=db)


# =============================================================
# DELETE /branch-subjects/branch/{branch_uid}/subject/{code}
# admin (own branch only) | super_admin
# =============================================================
@router.delete("/branch/{branch_uid}/subject/{code}")
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

    return delete_branch_subject_service(
        branch_uid=branch_uid,
        subject_code=code,
        db=db,
        enforced_branch_uid=enforced_branch_uid
    )