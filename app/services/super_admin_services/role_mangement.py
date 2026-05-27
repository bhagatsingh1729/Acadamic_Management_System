from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminCreate,
    AdminUpdate,
    AdminResponse
)
from fastapi import HTTPException
from app.crud.fundamental_crud.admin_crud import (
    create_admin
)
from app.core.security import hash_password
from app.models.models import Branch,Admin,User
from sqlalchemy.orm import Session
from app.schemas.fundamental_schemas import admin_schema
from app.schemas.services_schemas.super_admin_schemas.role_management import (
    AdminResponse
)
from app.crud.fundamental_crud.admin_crud import (
    create_admin,
    update_admin
)
def create_admin_service(data:AdminCreate,db:Session):

    branch_uid = data.branch_uid.upper()
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404,detail='branch not found')
    data_payload = admin_schema.AdminCreate(
        name=data.name,
        email=data.email,
        password=data.password,
        branch_id=branch_db.id,
        phone_no=data.phone_no,
        dob=data.dob,
        address=data.address
    )
    return create_admin(db=db,admin_data=data_payload)

def get_all_admin_service(db:Session):
    admins = db.query(Admin).all()
    if not admins:
        raise HTTPException(status_code=400,detail='no admin found')
    return admins

    
