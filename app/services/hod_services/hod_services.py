from app.crud.fundamental_crud.hod_crud import (
    create_hod,
    delete_hod,
)
from pydantic import EmailStr
from app.schemas.services_schemas.role_management_schemas.hod_schemas import (
    CreateHodRequest,
    HodAccountResponse,
)
from app.schemas.response_schemas.base_response import UserBasicInfo
from app.models.models import HOD,Department,User
from app.schemas.fundamental_schemas.hod_schema import (
    HodCreate,
)
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

def create_hod_service(data: CreateHodRequest, db: Session):
    dept_uid_upper = data.dept_uid.upper()
    db_dept = db.query(Department).filter(Department.dept_uid == dept_uid_upper).first()
    if not db_dept:
        raise HTTPException(status_code=404, detail='Department not found')
    
    data_payload = HodCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        department_id=db_dept.id
    )

    try:
        result = create_hod(db=db, data=data_payload)
        db.commit()
        #db.refresh(result)

        return HodAccountResponse.model_validate(result)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def get_all_hods_service(db: Session):
    hods = db.query(HOD).options(
        joinedload(HOD.department),
        joinedload(HOD.user)
    ).all()

    if not hods:
        raise HTTPException(status_code=404, detail="No HODs found")
        
    # Instead of manual instantiation, use model_validate
    return [
        HodAccountResponse.model_validate(hod) for hod in hods
    ]

def delete_hod_service(email: str, db: Session):
    db_user = db.query(User).filter(User.email == email, User.role == 'hod').first()
    if not db_user:
        raise HTTPException(status_code=404, detail="HOD not found")
    
    try:
        if db_user.hod:
            db.delete(db_user.hod)
        db.delete(db_user)
        db.commit()
        return {"message": "HOD deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to delete HOD: {str(e)}")