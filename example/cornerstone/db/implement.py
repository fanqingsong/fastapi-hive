

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from fastapi import FastAPI
from example.cornerstone.config import DATABASE_URL
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper
from fastapi_sqlalchemy import db  # an object to provide global access to a database session


Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def add_db_middleware(app: FastAPI):
    app.add_middleware(DBSessionMiddleware, db_url=DATABASE_URL)

    app.state.db = db


def create_all_tables(app: FastAPI):
    Base.metadata.create_all(engine)  # Create tables
    print("-- call create all over ----")



