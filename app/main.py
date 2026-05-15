from fastapi import FastAPI
from app.api.user_routes import router_user
from app.api.branch_routes import router_branch
from app.api.department_routes import router_department
from app.api.subject_routes import router_subject
from app.middleware.custom_middleware import TimeMiddleware
from app.database import Base,engine
from app.core.exception_handler import register_exception_handlers

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API", description="API for managing student records")

app.add_middleware(TimeMiddleware)  

app.include_router(router_user)
app.include_router(router_branch)
app.include_router(router_department)  
app.include_router(router_subject)  

register_exception_handlers(app)
