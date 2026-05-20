from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.department_schema import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)

from app.crud.fundamental_crud.department_crud import (
    create_department,
    get_all_departments,
    get_department_by_id,
    update_department,
    delete_department
)

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


# ------------------------------------------------
# CREATE DEPARTMENT
# ------------------------------------------------
@router.post("/", response_model=DepartmentResponse)
def create_department_route(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db)
):

    try:
        return create_department(
            db,
            department_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ------------------------------------------------
# GET ALL DEPARTMENTS
# ------------------------------------------------
@router.get("/", response_model=list[DepartmentResponse])
def get_all_departments_route(
    db: Session = Depends(get_db)
):

    return get_all_departments(db)


# ------------------------------------------------
# GET SINGLE DEPARTMENT
# ------------------------------------------------
@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department_route(
    department_id: int,
    db: Session = Depends(get_db)
):

    try:
        return get_department_by_id(
            db,
            department_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


# ------------------------------------------------
# UPDATE DEPARTMENT
# ------------------------------------------------
@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department_route(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db)
):

    try:
        return update_department(
            db,
            department_id,
            department_data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ------------------------------------------------
# DELETE DEPARTMENT
# ------------------------------------------------
@router.delete("/{department_id}")
def delete_department_route(
    department_id: int,
    db: Session = Depends(get_db)
):

    try:
        return delete_department(
            db,
            department_id
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )