from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.dialects.mysql import reflection

from models import Users
from .auth import get_current_user
from .dependencies import db_dependency
from pwdlib import PasswordHash

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

user_dependency =Annotated[Users,Depends(get_current_user)]

password_hash =  PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)

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

class PasswordChangeRequest(BaseModel):
    password:str
    new_password:str=Field(min_length=8)

class UpdatePhoneNumberRequest(BaseModel):
    phone_number:str|None

@router.get("/",status_code=status.HTTP_200_OK)
async def get_user(user:user_dependency,db:db_dependency):
    user = db.scalar(select(Users).where(Users.id==user.id))
    return UserOut.model_validate(user)

@router.patch("/change_password",status_code=status.HTTP_201_CREATED)
async def change_password(user:user_dependency,
                          db:db_dependency,
                          password_change_request:PasswordChangeRequest
                          ):
    user:Users|None= db.scalar(select(Users).where(Users.id == user.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not password_hash.verify(password_change_request.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error on password change",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.hashed_password = hash_password(password_change_request.new_password)

    db.add(user)
    db.commit()
    db.refresh(user)

@router.patch("/phonenumber/{phone_number}")
async def update_phone_number(user:user_dependency,
                              db:db_dependency,
                              update_phone_number_request:UpdatePhoneNumberRequest
                              ):
    user:Users|None= db.scalar(select(Users).where(Users.id == user.id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.phone_number = update_phone_number_request.phone_number

    db.add(user)
    db.commit()
    db.refresh(user)
