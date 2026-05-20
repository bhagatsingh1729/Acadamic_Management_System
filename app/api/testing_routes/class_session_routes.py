# =========================================================
# class_session_routes.py
# =========================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.class_session_schema import (
    ClassSessionCreate,
    ClassSessionResponse
)

from app.crud.fundamental_crud.class_session_crud import (
    create_class_session,
    get_all_class_sessions,
    get_class_session_by_id,
    delete_class_session
)

router = APIRouter(
    prefix="/class-sessions",
    tags=["Class Sessions"]
)


@router.post("/", response_model=ClassSessionResponse)
def create_session(data: ClassSessionCreate, db: Session = Depends(get_db)):

    try:
        return create_class_session(db, data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ClassSessionResponse])
def get_sessions(db: Session = Depends(get_db)):
    return get_all_class_sessions(db)


@router.get("/{session_id}", response_model=ClassSessionResponse)
def get_session(session_id: int, db: Session = Depends(get_db)):

    try:
        return get_class_session_by_id(db, session_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):

    try:
        return delete_class_session(db, session_id)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))