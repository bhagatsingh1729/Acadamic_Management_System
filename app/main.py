from fastapi import FastAPI
from app.api.user_routes import router_user
from app.middleware.custom_middleware import TimeMiddleware
from app.database import Base,engine
from app.core.exception_handler import register_exception_handlers

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API", description="API for managing student records")

app.add_middleware(TimeMiddleware)  # Fix: include the time middleware

app.include_router(router_user)

register_exception_handlers(app)
