from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks
from fastapi_hive.ioc_framework.decorators import cornerstone, provides, request_provides
from example.cornerstone.db.implement import Base, create_all_tables, add_db_middleware
from fastapi_sqlalchemy import db


__all__ = ['Base']


class LazyDBSession:
    """Resolve the scoped session when the route runs, after DB middleware."""

    def __init__(self, database):
        self._database = database

    def __getattr__(self, name):
        return getattr(self._database.session, name)


@cornerstone(name="db", order=0)
class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self):
        super(CornerstoneHooksImpl, self).__init__()

    @provides("db")
    def configure(self):
        print("call configure from cornerstone db!!!")

        add_db_middleware(self.app, self.cornerstone)

        self.app_state['db'] = db
        return db

    def post_endpoint_startup(self):
        print("call post startup from cornerstone!!!")

        create_all_tables(self.app)

    def pre_endpoint_shutdown(self):
        print("call pre shutdown from cornerstone!!!")

    def post_endpoint_shutdown(self):
        print("call pre shutdown from cornerstone!!!")

    @request_provides("db.session")
    def pre_endpoint_call(self):
        print("call pre endpoint call from cornerstone!!!")

        self.request_state['db'] = db
        return LazyDBSession(db)

    def post_endpoint_call(self):
        print("call post endpoint call from cornerstone!!!")
