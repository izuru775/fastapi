from typing import Annotated

from pydantic import BaseModel, Field
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, status, Path,Request

from models import Todos, Users
from .auth import get_current_user
from .dependencies import db_dependency
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from config import Settings, get_settings

templates =Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)
user_dependency =Annotated[Users,Depends(get_current_user)]

class TodoRequest(BaseModel):
    title:str= Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int = Field(gt=0,lt=6)
    complete:bool

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page",status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages ###
@router.get("/todo-page")
async def render_todo_page(request:Request,db:db_dependency):
    try:
        user = await get_current_user(token=request.cookies.get("access_token",""),db=db,settings=get_settings())
        if user is None:
            return redirect_to_login()
        print(user.id)
        todos = db.scalars(select(Todos).where(Todos.owner_id==user.id)).all()
        return templates.TemplateResponse(name="todo.html",request=request,context={"todos":todos})
    except:
        return redirect_to_login()

### Endpoints ###
@router.get("/",status_code=status.HTTP_200_OK)
async def read_all(user:user_dependency,db:db_dependency):
    return db.scalars(select(Todos).where(Todos.owner_id==user.id)).all()

@router.get("/todo/{todo_id}",status_code=status.HTTP_200_OK)
async def read_todo(user:user_dependency,db:db_dependency,todo_id:int=Path(gt=0)):
    todo_model :Todos |None = db.scalar(select(Todos).where((Todos.owner_id==user.id) & (Todos.id==todo_id)))
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="Todo not found")

@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dependency,
                      db:db_dependency,
                      todo_request:TodoRequest):
    todo_model = Todos(**todo_request.model_dump(),owner_id=user.id)

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)

    return {"message":"Todo created successfully","todo_id":todo_model.id}

@router.put("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dependency,
                      db:db_dependency,
                      todo_request:TodoRequest,
                      todo_id:int= Path(gt=0)):
    todo_model :Todos |None = db.scalar(select(Todos).where((Todos.id==todo_id)&(Todos.owner_id==user.id)))
    if todo_model is not None:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete

        db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404,detail="Todo not found")

@router.delete("/todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dependency,
                      db:db_dependency,
                      todo_id:int=Path(gt=0)):
    todo_model:Todos |None = db.scalar(select(Todos).where((Todos.id==todo_id )& (Todos.owner_id==user.id)))

    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")

    db.delete(todo_model)
    db.commit()



