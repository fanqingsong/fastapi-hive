from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
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
    def pre_endpoint_setup(self):
        print("call pre setup from cornerstone db!!!")

        add_db_middleware(self.app, self.cornerstone)

        self.app_state['db'] = db
        return db

    def post_endpoint_setup(self):
        print("call post setup from cornerstone!!!")

        create_all_tables(self.app)

    def pre_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")

    @request_provides("db.session")
    def pre_endpoint_call(self):
        print("call pre endpoint call from cornerstone!!!")

        self.request_state['db'] = db
        return LazyDBSession(db)

    def post_endpoint_call(self):
        print("call post endpoint call from cornerstone!!!")


@cornerstone(name="db", order=0)
class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self):
        super(CornerstoneAsyncHooksImpl, self).__init__()

    async def pre_endpoint_setup(self):
        print("call pre setup from cornerstone async!!!")

    async def post_endpoint_setup(self):
        print("call post setup from cornerstone async!!!")

    async def pre_endpoint_teardown(self):
        print("call pre teardown from cornerstone async!!!")

    async def post_endpoint_teardown(self):
        print("call pre teardown from cornerstone async!!!")

    async def pre_endpoint_call(self):
        print("call pre endpoint call from cornerstone async!!!")

    async def post_endpoint_call(self):
        print("call post endpoint call from cornerstone async!!!")
