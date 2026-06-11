from app.services.hod_services.hod_services import (
    create_hod_service,
    get_all_hods_service,
    delete_hod_service,
)
from pydantic import EmailStr
from fastapi import HTTPException,Depends,APIRouter
from app.database import get_db
from app.core.dependencies import require_roles
from app.schemas.services_schemas.role_management_schemas.hod_schemas import (
    CreateHodRequest,
    HodAccountResponse,
)
from sqlalchemy.orm import Session
from app.schemas.response_schemas.API_Response import ApiResponse
from typing import List

router = APIRouter(prefix="/hod",tags=["HOD Management"])

@router.post("/create", response_model=ApiResponse[HodAccountResponse])
def create_hod_route(data: CreateHodRequest, db: Session = Depends(get_db), current_user=Depends(require_roles('super_admin'))):
    # Authorization logic is handled by require_roles, 
    # redundant check removed for cleaner code
    result = create_hod_service(data=data, db=db)
    return ApiResponse(success=True,message='HOD created successfully',data=result)

@router.get("/all", response_model=ApiResponse[List[HodAccountResponse]])
def get_all_hods_route(db: Session = Depends(get_db), current_user=Depends(require_roles('super_admin'))):
    result = get_all_hods_service(db=db)
    return ApiResponse(success=True,message='HOD list',data=result)

@router.delete("/delete/{email}",response_model=ApiResponse[None])
def delete_hod_route(email: EmailStr, db: Session = Depends(get_db), current_user=Depends(require_roles('super_admin'))):
    # Corrected: passed email variable to the service
    delete_hod_service(email=email, db=db)
    return ApiResponse(success=True,message='HOD deleted successfully',data=None)