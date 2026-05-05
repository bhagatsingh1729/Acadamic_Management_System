from fastapi import FastAPI
from app.database import Base, engine
from app.core.exception_handler import register_exception_handlers
from app.middleware.custom_middleware import TimeMiddleware  # Fix: added missing import for TimeMiddleware
from app.routes.routes import router  # Fix: removed duplicate import of router
# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management API", description="API for managing student records", version="1.0.0")

app.add_middleware(TimeMiddleware)  # Fix: include the time middleware

app.include_router(router, tags=["students"])

register_exception_handlers(app)
