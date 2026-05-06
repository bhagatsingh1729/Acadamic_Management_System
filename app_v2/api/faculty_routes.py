from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app_v2.database import get_db
from typing import List
from app_v2.schemas.user_schema import FacultyCreate, FacultyRead
from app_v2.crud.user_crud import create_faculty

router_faculty = APIRouter()



@router_faculty.post("/create-faculty", response_model=FacultyRead)
def create_faculty_route(faculty: FacultyCreate, db: Session = Depends(get_db)):
    return create_faculty(db, faculty)