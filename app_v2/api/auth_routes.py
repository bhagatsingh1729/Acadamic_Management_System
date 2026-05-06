from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app_v2.utils.auth_utils import create_access_token, verify_token
from app_v2.utils.utils import get_user
from app_v2.core.security import verify_password
from app_v2.database import get_db

router_auth = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@router_auth.post('/token')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(email=form_data.username, db=db)
    if not user:
        raise HTTPException(status_code=400, detail='Invalid username or password')
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail='Invalid username or password')
    
    access_token = create_access_token(data={'sub': user.email})
    return {'access_token': access_token, 'token_type': 'bearer'}


@router_auth.get('/users')
def read_users(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    return {'username': username}