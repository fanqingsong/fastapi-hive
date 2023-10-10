
from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_model import Endpoint, EndpointAsync
# from demo.yyy_endpoint.house_price2.router import router
from demo.yyy_endpoint.house_price2.service import service


class EndpointImpl(Endpoint):

    def __init__(self, app: FastAPI):
        super(EndpointImpl, self).__init__(app)

    def setup(self):
        print("call pre setup from EndpointImpl!!!")
        print("---- get fastapi app ------")
        print(self._app)

    def teardown(self):
        print("call pre teardown from EndpointImpl!!!")


class EndpointAsyncImpl(EndpointAsync):

    def __init__(self, app: FastAPI):
        super(EndpointAsyncImpl, self).__init__(app)

    async def setup(self):
        print("call pre setup from cornerstone EndpointAsyncImpl!!!")

    async def teardown(self):
        print("call pre teardown from cornerstone EndpointAsyncImpl!!!")

