from fastapi import FastAPI

from app.api.v1.auth_routes import router as auth_router
from app.api.v1.user_routes import router as user_router
app = FastAPI(
    title="University Management System API",
    description="API for managing university operations, including students, faculty, courses, and more.",
)

app.include_router(auth_router)
app.include_router(user_router)