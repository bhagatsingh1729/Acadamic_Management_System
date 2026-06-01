# =============================================================
# services/student_services/student_service.py
#
# Handles all student business logic and ownership validation.
# =============================================================
#
# WHAT THIS SERVICE DOES:
#
# 1. Resolves human identifiers to DB IDs
#    branch_uid="CSE" → branch_id=3
#
# 2. Enforces ownership rules (RBAC Layer 3)
#    Admin from CSE cannot create students in ECE.
#    Admin from CSE cannot view students from ECE.
#
# 3. Calls CRUD with resolved IDs
#    The CRUD never deals with branch_uid — only integers.
#
# OWNERSHIP PARAMETER EXPLAINED:
#   enforced_branch_id: Optional[int]
#     - When set (admin role): service REJECTS any request
#       where the resolved branch != admin's own branch.
#     - When None (super_admin role): no branch restriction.
#       Super admin can manage students in any branch.
#
# =============================================================

from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.crud.fundamental_crud.student_crud import (
    create_student,
    get_student_by_id,
    get_student_by_usn,
    get_all_students,
    get_students_by_branch,
    get_students_by_cohort,
    update_student,
    delete_student,
)
from app.crud.fundamental_crud.branch_crud import get_branch_by_uid
from app.schemas.fundamental_schemas.student_schema import StudentCreate, StudentUpdate
from app.schemas.services_schemas.role_management_schemas.student_schemas import (
    StudentCreateRequest,
    StudentUpdateRequest
)
from app.models.models import Branch


# =============================================================
# CREATE STUDENT
# =============================================================
def create_student_service(
    db: Session,
    data: StudentCreateRequest,
    enforced_branch_id: Optional[int] = None
    # ↑ Passed from route:
    #   admin role  → admin.branch_id   (branch-scoped)
    #   super_admin → None              (unrestricted)
):
    # ─── Step 1: Resolve branch_uid → branch object ──────────
    branch = get_branch_by_uid(db, data.branch_uid)

    if not branch:
        raise HTTPException(
            status_code=404,
            detail=f"Branch '{data.branch_uid}' not found"
        )

    # ─── Step 2: Ownership check (RBAC Layer 3) ───────────────
    # If enforced_branch_id is set, this is an admin request.
    # Admin can ONLY create students for their own branch.
    # If they try to create for another branch → 403.
    if enforced_branch_id is not None:
        if branch.id != enforced_branch_id:
            raise HTTPException(
                status_code=403,
                detail="You can only create students for your own branch"
            )

    # ─── Step 3: Build the CRUD-level schema with resolved ID ─
    student_create_data = StudentCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        usn=data.usn,
        semester=data.semester,
        batch=data.batch,
        section=data.section,
        branch_id=branch.id,      # ← resolved from branch_uid
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )

    # ─── Step 4: Call CRUD ────────────────────────────────────
    return create_student(db, student_create_data)


# =============================================================
# GET ALL STUDENTS
# =============================================================
def get_all_students_service(
    db: Session,
    enforced_branch_id: Optional[int] = None
    # admin → only their branch students
    # super_admin, faculty, hod → all students
):
    if enforced_branch_id is not None:
        # Admin only sees their own branch's students
        return get_students_by_branch(db, enforced_branch_id)

    return get_all_students(db)


# =============================================================
# GET STUDENT BY USN
# =============================================================
def get_student_by_usn_service(
    db: Session,
    usn: str,
    enforced_branch_id: Optional[int] = None
):
    student = get_student_by_usn(db, usn)
    # ↑ raises HTTPException(404) if not found

    # ─── Ownership check ──────────────────────────────────────
    # Admin can only view students from their own branch.
    if enforced_branch_id is not None:
        if student.branch_id != enforced_branch_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view students from your own branch"
            )

    return student


# =============================================================
# GET STUDENTS BY COHORT
# =============================================================
def get_students_by_cohort_service(
    db: Session,
    semester: int,
    batch: str,
    section: str,
    enforced_branch_id: int     # always required for cohort queries
):
    return get_students_by_cohort(
        db,
        branch_id=enforced_branch_id,
        semester=semester,
        batch=batch,
        section=section
    )


# =============================================================
# UPDATE STUDENT  ← THIS IS WHERE THE FIX LIVES
# =============================================================
def update_student_service(
    db: Session,
    usn: str,
    data: StudentUpdateRequest,
    enforced_branch_id: Optional[int] = None
):
    # Step 1: Fetch student by USN (raises 404 if not found)
    student = get_student_by_usn(db, usn)

    # Step 2: Ownership check
    if enforced_branch_id is not None:
        if student.branch_id != enforced_branch_id:
            raise HTTPException(
                status_code=403,
                detail="You can only update students from your own branch"
            )

    # Step 3: Extract ONLY the fields the client actually sent
    # ─────────────────────────────────────────────────────────
    # This is the KEY fix.
    # model_dump(exclude_unset=True) gives you a dict with only
    # the keys the client included in the request body.
    #
    # Client sends: { "semester": 5 }
    # raw = { "semester": 5 }          ← only this, nothing else
    #
    # Old broken code was doing StudentUpdate(semester=5, batch=None, ...)
    # which made Pydantic think batch was SET to None.
    # Now we only pass what was actually sent.
    # ─────────────────────────────────────────────────────────
    raw = data.model_dump(exclude_unset=True)

    # Step 4: Resolve branch_uid → branch_id if client sent it
    # ─────────────────────────────────────────────────────────
    # We pop branch_uid out (CRUD schema doesn't know about it)
    # and replace it with the resolved branch_id integer.
    # If client didn't send branch_uid, we skip this entirely.
    # ─────────────────────────────────────────────────────────
    if "branch_uid" in raw:
        branch_uid = raw.pop("branch_uid").upper()
        branch_db = db.query(Branch).filter(
            Branch.branch_uid == branch_uid
        ).first()
        if not branch_db:
            raise HTTPException(
                status_code=404,
                detail=f"Branch '{branch_uid}' not found"
            )
        raw["branch_id"] = branch_db.id

    # Step 5: Build StudentUpdate with only the resolved fields
    # Pydantic will correctly mark everything else as unset
    update_data = StudentUpdate(**raw)

    # Step 6: Call CRUD
    return update_student(db, student.id, update_data)


# =============================================================
# DELETE STUDENT
# =============================================================
def delete_student_service(
    db: Session,
    usn: str,
    enforced_branch_id: Optional[int] = None
):
    student = get_student_by_usn(db, usn)

    if enforced_branch_id is not None:
        if student.branch_id != enforced_branch_id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete students from your own branch"
            )

    return delete_student(db, student.id)
