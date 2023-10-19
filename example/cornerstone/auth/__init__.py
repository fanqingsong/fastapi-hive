
from fastapi import FastAPI
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
from example.cornerstone.auth.implement import validate_request


class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self):
        super(CornerstoneHooksImpl, self).__init__()

    def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)

    def post_endpoint_setup(self):
        print("call post setup from CornerstoneHooksImpl!!!")

    def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")

    def pre_endpoint_call(self):
        pass

    def post_endpoint_call(self):
        pass


class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self):
        super(CornerstoneAsyncHooksImpl, self).__init__()

    async def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_setup(self):
        print("call post setup from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_call(self):
        pass

    async def post_endpoint_call(self):
        pass
