from datetime import timedelta, datetime, timezone
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from config import Settings, get_settings
from models import Users
from pwdlib import PasswordHash
from .dependencies import db_dependency

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


oauth2_scheme =OAuth2PasswordBearer(tokenUrl="auth/token")


class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str
    phone_number:str|None

class Token(BaseModel):
    access_token:str
    token_type:str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:int
    email:str
    username:str
    first_name:str
    last_name:str
    is_active:bool
    role:str|None
    phone_number:str|None

password_hash =  PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)


def authenticate_user(username:str,password:str,db:db_dependency)->None|Users:
    user:Users|None = db.scalar(select(Users).where(Users.username==username))
    if not user:
        return None
    if not password_hash.verify(password,user.hashed_password):
        return None
    return user

def create_access_token(data:dict,settings: Annotated[Settings, Depends(get_settings)],expires_delta:timedelta|None=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc)+expires_delta
    else:
        expire = datetime.now(timezone.utc)+timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encode_jwt= jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    return encode_jwt

async def get_current_user(token:Annotated[str,Depends(oauth2_scheme)],db:db_dependency,settings: Annotated[Settings, Depends(get_settings)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        username:str=payload.get("sub")
        user_id:int=payload.get("id")
        if username is None or user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    user = db.scalar(select(Users).where(Users.id == user_id))
    if user is None:
        raise credentials_exception
    return UserOut.model_validate(user)


@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,
                      create_user_request:CreateUserRequest):
    user_model:Users = Users(
        username = create_user_request.username,
        email=create_user_request.email,
        first_name= create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password= hash_password(create_user_request.password),
        role=create_user_request.role,
        phone_number=create_user_request.phone_number,
        is_active=True
    )
    try:
        db.add(user_model)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        return {"error":"Duplicate or bad constraint","description":e.orig}
    except SQLAlchemyError as e:
        return {"error":"A database error occurred","description":str(e)}

@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_dependency,
                                 settings: Annotated[Settings, Depends(get_settings)]):
    user:None|Users = authenticate_user(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user.username,"id":user.id},settings=settings, expires_delta=access_token_expires)
    return Token(access_token=access_token,token_type="bearer")
