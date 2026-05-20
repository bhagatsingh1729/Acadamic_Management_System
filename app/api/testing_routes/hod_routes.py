# =========================================================
# hod_routes.py
# =========================================================

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.fundamental_schemas.hod_schema import (
    HodCreate,
    HodResponse
)

from app.crud.fundamental_crud.hod_crud import (
    create_hod,
    get_all_hods,
    get_hod_by_id,
    delete_hod
)

router = APIRouter(
    prefix="/hods",
    tags=["HOD"]
)


@router.post(
    "/",
    response_model=HodResponse
)
def create_new_hod(
    data: HodCreate,
    db: Session = Depends(get_db)
):

    try:

        return create_hod(
            db,
            data
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=list[HodResponse]
)
def get_hods(
    db: Session = Depends(get_db)
):

    return get_all_hods(db)


@router.get(
    "/{hod_id}",
    response_model=HodResponse
)
def get_single_hod(
    hod_id: int,
    db: Session = Depends(get_db)
):

    try:

        return get_hod_by_id(
            db,
            hod_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete("/{hod_id}")
def remove_hod(
    hod_id: int,
    db: Session = Depends(get_db)
):

    try:

        return delete_hod(
            db,
            hod_id
        )

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )