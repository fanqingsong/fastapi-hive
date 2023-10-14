import logging

from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneHooks, CornerstoneAsyncHooks
from example.cornerstone.db.implement import Base, create_all_tables, add_db_middleware
from fastapi import FastAPI


__all__ = ['Base', 'CornerstoneHooksImpl', 'CornerstoneAsyncHooksImpl']


class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self, app: FastAPI):
        super(CornerstoneHooksImpl, self).__init__(app)

    def pre_endpoint_setup(self):
        print("call pre setup from cornerstone db!!!")

        add_db_middleware(self._app)

    def post_endpoint_setup(self):
        print("call post setup from cornerstone!!!")

        create_all_tables(self._app)

    def pre_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")


class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self, app: FastAPI):
        super(CornerstoneAsyncHooksImpl, self).__init__(app)

    async def pre_endpoint_setup(self):
        print("call pre setup from cornerstone async!!!")

    async def post_endpoint_setup(self):
        print("call post setup from cornerstone async!!!")

    async def pre_endpoint_teardown(self):
        print("call pre teardown from cornerstone async!!!")

    async def post_endpoint_teardown(self):
        print("call pre teardown from cornerstone async!!!")
