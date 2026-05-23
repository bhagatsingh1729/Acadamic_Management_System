from fastapi import FastAPI

from app.api.v1.auth_routes import router as auth_router

app = FastAPI(
    title="University Management System API",
    description="API for managing university operations, including students, faculty, courses, and more.",
)

app.include_router(auth_router)