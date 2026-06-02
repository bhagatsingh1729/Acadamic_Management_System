# =============================================================
# main.py
# =============================================================

from fastapi import FastAPI

# ── Database ──────────────────────────────────────────────────
from app.database import engine, Base

# ── Import ALL models so SQLAlchemy registers every table ────
from app.models.models import (
    User, Student, Faculty, Admin, HOD, SuperAdmin,
    Branch, Department, Subject,
    BranchSubject, FacultySubject, StudentSubject,
    ClassSession, Attendance, Exam, Marks
)

# ── Core ──────────────────────────────────────────────────────
from app.core.exception_handler import register_exception_handlers
from app.middleware.custom_middleware import TimeMiddleware

# ── Routes ────────────────────────────────────────────────────
from app.api.v1.auth_routes.auth_routes import router as auth_router
from app.api.v1.user_routes.user_routes import router as user_router
from app.api.v1.student_routes.student_routes import router as student_router
from app.api.v1.branch_routes.branch_routes import router as branch_router
from app.api.v1.department_routes.department_routes import router as department_router
from app.api.v1.faculty_routes.faculty_routes import router as faculty_router
from app.api.v1.admin_routes.admin_routes import router as admin_router
from app.api.v1.subject_routes.subject_routes import router as subject_router
from app.api.v1.subject_routes.branch_subject_routes import router as assign_subject_router
from app.api.v1.subject_routes.student_subject_routes import router as student_subject_router
from app.api.v1.subject_routes.faculty_subject_routes import router as faculty_subject_router
# ── Create all tables on startup ─────────────────────────────
Base.metadata.create_all(bind=engine)

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="College ERP API",
    description="College ERP backend — students, faculty, attendance, marks.",
    version="2.0.0",
)

# ── Middleware ────────────────────────────────────────────────
app.add_middleware(TimeMiddleware)

# ── Exception Handlers ───────────────────────────────────────
register_exception_handlers(app)

# ── Register Routers ─────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth_router)                                    # /auth/login
app.include_router(user_router)                                    # /users/me
app.include_router(student_router, prefix=API_PREFIX)              # /api/v1/students
app.include_router(branch_router, prefix=API_PREFIX)               # /api/v1/branches
app.include_router(department_router, prefix=API_PREFIX)           # /api/v1/departments
app.include_router(faculty_router, prefix=API_PREFIX)              # /api/v1/faculty
app.include_router(admin_router, prefix=API_PREFIX)                # /api/v1/admin
app.include_router(subject_router,prefix=API_PREFIX)
app.include_router(assign_subject_router,prefix=API_PREFIX)
app.include_router(student_subject_router,prefix=API_PREFIX)
app.include_router(faculty_subject_router,prefix=API_PREFIX)
# NOTE: Add more routers here as each service is built.
# Example:
#   from app.api.v1.faculty_routes import router as faculty_router
#   app.include_router(faculty_router, prefix=API_PREFIX)
