from database import Base
from sqlalchemy import String,Integer,Boolean
from sqlalchemy.orm import Mapped, mapped_column

class Todos(Base):
    __tablename__="todos"

    id :Mapped[int]= mapped_column(Integer,primary_key=True,index=True)
    title:Mapped[str] = mapped_column(String)
    description:Mapped[str]= mapped_column(String,nullable=True)
    priority:Mapped[int]= mapped_column(Integer,nullable=True)
    complete:Mapped[bool] =mapped_column(Boolean,default=False,nullable=True)
