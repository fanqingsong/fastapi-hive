
from fastapi import FastAPI
from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneHooks, CornerstoneAsyncHooks


class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self, app: FastAPI):
        super(CornerstoneHooksImpl, self).__init__(app)

    def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self._app)

    def post_endpoint_setup(self):
        print("call post setup from CornerstoneHooksImpl!!!")

    def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")


class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self, app: FastAPI):
        super(CornerstoneAsyncHooksImpl, self).__init__(app)

    async def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_setup(self):
        print("call post setup from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

