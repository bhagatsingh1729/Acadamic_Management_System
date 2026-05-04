from fastapi import FastAPI
from app.routes import router,read_students,read_student,update_student_data,delete_student_data
from app.core.exception_handler import register_exception_handlers
app = FastAPI()
from app.database import Base,engine

Base.metadata.create_all(bind=engine)

app.include_router(router,tags=["students"])

register_exception_handlers(app)