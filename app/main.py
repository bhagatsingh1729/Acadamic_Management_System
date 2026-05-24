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
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.user_routes import router as user_router
from app.api.v1.student_routes import router as student_router

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

# NOTE: Add more routers here as each service is built.
# Example:
#   from app.api.v1.faculty_routes import router as faculty_router
#   app.include_router(faculty_router, prefix=API_PREFIX)
