from fastapi import FastAPI
from app.routes import router  # Fix: removed unnecessary individual route function imports
from app.database import Base, engine
from app.core.exception_handler import register_exception_handlers

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router, tags=["students"])

register_exception_handlers(app)
