from typing import Annotated

from fastapi import APIRouter, status, Depends
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from database import SessionLocal
from models import Users
from pwdlib import PasswordHash

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

class CreateUserRequest(BaseModel):
    username:str
    email:str
    first_name:str
    last_name:str
    password:str
    role:str

password_hash =  PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)

def authenticate_user(username:str,password:str,db:db_dependency):
    user:Users| None = db.scalar(select(Users).where(Users.username==username))
    if not user:
        return False
    return password_hash.verify(password,user.hashed_password)


@router.post("/auth",status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency,
                      create_user_request:CreateUserRequest):
    user_model:Users = Users(
        username = create_user_request.username,
        email=create_user_request.email,
        first_name= create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password= hash_password(create_user_request.password),
        role=create_user_request.role,
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

@router.post("/token")
async def login_for_access_token(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],
                                 db:db_dependency):
    is_authenticated = authenticate_user(form_data.username,form_data.password,db)
    return is_authenticated