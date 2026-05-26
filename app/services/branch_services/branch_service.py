from sqlalchemy.orm import Session

from app.schemas.services_schemas.branch_schema import (
    BranchCreate,
    BranchUpdate,
    BranchResponse
)
from app.models.models import Branch
from app.crud.fundamental_crud.branch_crud import (
    create_branch,
    update_branch,
    get_all_branches,
    get_branch_by_uid,
    get_branch_by_id,
    delete_branch
)
from fastapi import HTTPException

def create_branch_service(db:Session,data:BranchCreate):
    branch_exist = db.query(Branch).filter(Branch.branch_uid == data.branch_uid).first()
    # if branch exist raise error
    if branch_exist:
        raise HTTPException(status_code=409,detail='branch already exist')
    return create_branch(db,data)

def update_branch_service(branch_uid:str,data:BranchUpdate,db:Session):
    branch_db = db.query(Branch).filter(Branch.branch_uid == data.branch_uid).first()
    if branch_db:
        return update_branch(branch_id=branch_db.id,branch_data=data,db=db)
    
def get_all_branches_service(db:Session):
    return get_all_branches(db=db)

def get_branch_via_uid_service(branch_uid:str,db:Session):
    return get_branch_by_uid(branch_uid=branch_uid,db=db)

def delete_branch_service(branch_uid:str,db:Session):
    branch_db = db.query(Branch).filter(Branch.branch_uid == branch_uid).first()
    if not branch_db:
        raise HTTPException(status_code=404,detail='branch do not exist')
    return delete_branch(branch_id=branch_db.id,db=db)

