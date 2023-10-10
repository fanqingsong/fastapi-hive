
from fastapi import FastAPI
from fastapi_hive.ioc_framework.cornerstone_model import Cornerstone, CornerstoneAsync


class CornerstoneImpl(Cornerstone):

    def __init__(self, app: FastAPI):
        super(CornerstoneImpl, self).__init__(app)

    def pre_setup(self):
        print("call pre setup from cornerstone!!!")
        print("---- get fastapi app ------")
        print(self._app)

    def post_setup(self):
        print("call post setup from cornerstone!!!")

    def pre_teardown(self):
        print("call pre teardown from cornerstone!!!")

    def post_teardown(self):
        print("call pre teardown from cornerstone!!!")


class CornerstoneAsyncImpl(Cornerstone):

    def __init__(self, app: FastAPI):
        super(CornerstoneAsyncImpl, self).__init__(app)

    async def pre_setup(self):
        print("call pre setup from cornerstone async!!!")

    async def post_setup(self):
        print("call post setup from cornerstone async!!!")

    async def pre_teardown(self):
        print("call pre teardown from cornerstone async!!!")

    async def post_teardown(self):
        print("call pre teardown from cornerstone async!!!")

