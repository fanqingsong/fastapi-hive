
from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_model import EndpointHooks, EndpointAsyncHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self, app: FastAPI):
        super(EndpointHooksImpl, self).__init__(app)

    def setup(self):
        print("call pre setup from EndpointHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self._app)

    def teardown(self):
        print("call pre teardown from EndpointHooksImpl!!!")


class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self, app: FastAPI):
        super(EndpointAsyncHooksImpl, self).__init__(app)

    async def setup(self):
        print("call pre setup from EndpointAsyncHooksImpl!!!")

    async def teardown(self):
        print("call pre teardown from EndpointAsyncHooksImpl!!!")

