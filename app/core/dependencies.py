# =============================================================
# core/dependencies.py
# FastAPI dependency injection — auth + RBAC
# =============================================================
# Pattern:
#   get_current_user       → decodes JWT, returns User
#   require_roles(...)     → flexible role guard factory
#   require_X              → single-role shortcuts
#   get_current_admin      → resolves Admin record (has branch_id)
#   get_current_faculty    → resolves Faculty record
#   get_current_student    → resolves Student record
#   get_current_hod        → resolves HOD record
# =============================================================

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User, Admin, Faculty, Student, HOD
from app.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =============================================================
# STEP 1 — Resolve JWT → User
# =============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =============================================================
# STEP 2 — Flexible role guard factory
# =============================================================
# Usage:  current_user = Depends(require_roles("admin", "super_admin"))
# Returns the User object.
# =============================================================

def require_roles(*roles: str):
    """Return a dependency enforcing the caller holds one of the given roles."""

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role(s): {list(roles)}"
            )
        return current_user

    return _checker


# =============================================================
# STEP 3 — Single-role convenience shortcuts
# =============================================================

def require_super_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_hod(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "hod":
        raise HTTPException(status_code=403, detail="HOD access required")
    return current_user


def require_faculty(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "faculty":
        raise HTTPException(status_code=403, detail="Faculty access required")
    return current_user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    return current_user


# =============================================================
# STEP 4 — Role-record resolvers
# =============================================================
# Returns the role-specific DB record (not just User).
# Routes needing branch_id, employee_id, usn, etc. use these.
# =============================================================

def get_current_admin(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
) -> Admin:
    admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin profile not found")
    return admin


def get_current_faculty(
    current_user: User = Depends(require_faculty),
    db: Session = Depends(get_db)
) -> Faculty:
    faculty = db.query(Faculty).filter(Faculty.user_id == current_user.id).first()
    if not faculty:
        raise HTTPException(status_code=403, detail="Faculty profile not found")
    return faculty


def get_current_student(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
) -> Student:
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=403, detail="Student profile not found")
    return student


def get_current_hod(
    current_user: User = Depends(require_hod),
    db: Session = Depends(get_db)
) -> HOD:
    hod = db.query(HOD).filter(HOD.user_id == current_user.id).first()
    if not hod:
        raise HTTPException(status_code=403, detail="HOD profile not found")
    return hod
