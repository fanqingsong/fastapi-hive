import logging
import time
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
from example.cornerstone.db.implement import Base, create_all_tables, add_db_middleware
from fastapi import FastAPI
from starlette.requests import Request
from fastapi_sqlalchemy import db


__all__ = ['Base']


class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self):
        super(CornerstoneHooksImpl, self).__init__()

    def pre_endpoint_setup(self):
        print("call pre setup from cornerstone db!!!")

        add_db_middleware(self._app, self.cornerstone)

    def post_endpoint_setup(self):
        print("call post setup from cornerstone!!!")

        create_all_tables(self._app)

        app = self.app

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()
            request.state.db = db
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            print(f'process_time = {process_time}')
            return response

    def pre_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from cornerstone!!!")


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

