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

router = APIRouter(prefix="/hod",tags=["HOD Management"])

@router.post("/create", response_model=HodAccountResponse)
def create_hod_route(data: CreateHodRequest, db: Session = Depends(get_db), current_user=Depends(require_roles('super_admin'))):
    # Authorization logic is handled by require_roles, 
    # redundant check removed for cleaner code
    return create_hod_service(data=data, db=db)

@router.get("/all", response_model=list[HodAccountResponse])
def get_all_hods_route(db: Session = Depends(get_db), current_user=Depends(require_roles('super_admin'))):
    return get_all_hods_service(db=db)

@router.delete("/delete/{email}")
def delete_hod_route(email: EmailStr, db: Session = Depends(get_db), current_user=Depends(require_roles('super_admin'))):
    # Corrected: passed email variable to the service
    return delete_hod_service(email=email, db=db)