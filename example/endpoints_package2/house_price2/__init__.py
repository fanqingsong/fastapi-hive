
from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks, EndpointAsyncHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def startup(self):
        print("call pre startup from EndpointHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)

    def shutdown(self):
        print("call pre shutdown from EndpointHooksImpl!!!")


class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self):
        super(EndpointAsyncHooksImpl, self).__init__()

    async def startup(self):
        print("call pre startup from EndpointAsyncHooksImpl!!!")

    async def shutdown(self):
        print("call pre shutdown from EndpointAsyncHooksImpl!!!")

