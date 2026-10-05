from fastapi import FastAPI
from fastapi_sqlalchemy import db

from fastapi_hive.ioc_framework.foundation_hooks import FoundationHooks
from fastapi_hive.ioc_framework.decorators import (
    autoconfigure,
    conditional,
    foundation,
    provides,
)
from fastapi_hive.ioc_framework.registry import Inject
from example.foundation.db.implement import Base, create_all_tables, add_db_middleware


__all__ = ['Base']


class LazyDBSession:
    """Resolve the scoped session when the route runs, after DB middleware."""

    def __init__(self, database):
        self._database = database

    def __getattr__(self, name):
        return getattr(self._database.session, name)


@autoconfigure(name="hive.db", order=0)
@conditional(on_import="fastapi_sqlalchemy", enabled_when="db")
class SqlAlchemyAuto:

    def configure(self, app: FastAPI):
        add_db_middleware(app, None)

    @provides("db")
    def engine(self):
        return db

    @provides("db.session", scope="request")
    def session(self, database=Inject("db")):
        return LazyDBSession(database)


@foundation(name="db", order=0)
class FoundationHooksImpl(FoundationHooks):

    def after_endpoint_startup(self):
        create_all_tables(self.app)
