from fastapi import FastAPI
#from app.api import auth_routes
from app.middleware.custom_middleware import TimeMiddleware
from app.database import Base,engine
from app.core.exception_handler import register_exception_handlers
from app.api.testing_routes import (
    super_admin_routes,
    user_routes,
    branch_routes,
    department_routes,
    subject_routes,
    student_routes,
    faculty_routes,
    admin_routes,
    faculty_subject_routes,
    branch_subject_routes,
    attendance_routes,
    class_session_routes,
    student_subject,
    hod_routes,
    exam_routes,
    marks_routes
)


# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API", description="API for managing student records")

app.add_middleware(TimeMiddleware)  

#app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(branch_routes.router)
app.include_router(department_routes.router)
app.include_router(subject_routes.router)
app.include_router(exam_routes.router)
app.include_router(student_routes.router)
app.include_router(hod_routes.router)
app.include_router(faculty_routes.router)
app.include_router(admin_routes.router)
app.include_router(class_session_routes.router)
app.include_router(attendance_routes.router)
app.include_router(marks_routes.router)
app.include_router(super_admin_routes.router) # testing routes for super admin, can be removed later

#junction tables related routes
app.include_router(student_subject.router)
app.include_router(faculty_subject_routes.router)
app.include_router(branch_subject_routes.router)

    
register_exception_handlers(app)
