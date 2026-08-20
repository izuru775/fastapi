from fastapi import APIRouter,status
from pydantic import BaseModel
from models import Users
from pwdlib import PasswordHash

router = APIRouter()

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

@router.post("/auth",status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request:CreateUserRequest):
    create_user_model:Users = Users(
        username = create_user_request.username,
        email=create_user_request.email,
        first_name= create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password= hash_password(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )


    return create_user_model