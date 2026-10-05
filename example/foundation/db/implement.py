

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI
from example.foundation.config import DATABASE_URL
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session

from fastapi_hive.ioc_framework.foundation_container import FoundationMeta

Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def add_db_middleware(app: FastAPI, foundation: FoundationMeta):
    app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)

    # foundation.state['db'] = db


def create_all_tables(app: FastAPI):
    Base.metadata.create_all(engine)  # Create tables
    print("-- call create all over ----")



