
from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks, EndpointAsyncHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def setup(self):
        print("call pre setup from EndpointHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)

    def teardown(self):
        print("call pre teardown from EndpointHooksImpl!!!")


class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self):
        super(EndpointAsyncHooksImpl, self).__init__()

    async def setup(self):
        print("call pre setup from EndpointAsyncHooksImpl!!!")

    async def teardown(self):
        print("call pre teardown from EndpointAsyncHooksImpl!!!")

