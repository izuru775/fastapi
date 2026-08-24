from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import Settings,get_settings

settings = get_settings()
SQLALCHEMY_DATABASE_URL=settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False})

SessionLocal =sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base = declarative_base()