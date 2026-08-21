from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status, Path
from models import Todos, Users
from .auth import get_current_user
from .dependencies import db_dependency


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)
user_dependency =Annotated[Users,Depends(get_current_user)]

@router.get("/todo",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    if not user.role.casefold() == "admin":
        raise HTTPException(status_code=401,detail="Authentication Failed")
    return db.scalars(select(Todos)).all()


@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,db:db_dependency,todo_id:int=Path(get=0)):
    if not user.role.casefold()=="admin":
        raise HTTPException(status_code=401,detail="Authentication Failed")

    todo_model = db.scalar(select(Todos).where(Todos.id==todo_id))

    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")

    db.delete(todo_model)
    db.commit()