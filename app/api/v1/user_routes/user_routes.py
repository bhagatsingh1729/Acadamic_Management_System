# app/api/user_routes.py
from fastapi import APIRouter, Depends
from app.models.models import User
from app.core.dependencies import get_current_user  # 👈 Import your dependency


router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):  # 👈 Use it here
    return {"id": current_user.id, "email": current_user.email, "name":current_user.name, "role":current_user.role}
    
