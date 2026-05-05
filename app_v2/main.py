from fastapi import FastAPI
from app_v2.database import Base, engine
from app_v2.core.exception_handler import register_exception_handlers
from app_v2.middleware.custom_middleware import TimeMiddleware  # Fix: added missing import for TimeMiddleware
from app_v2.api.user_routes import router_user  # Fix: removed duplicate import of router
# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API", description="API for managing student records", version="1.0.0")

app.add_middleware(TimeMiddleware)  # Fix: include the time middleware

app.include_router(router_user, tags=["users"])

register_exception_handlers(app)
