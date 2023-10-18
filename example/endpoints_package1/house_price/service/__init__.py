

from example.endpoints_package1.house_price.service.implement import HousePriceModel

from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH

from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks, EndpointAsyncHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def setup(self):
        print("call pre setup from EndpointHooksImpl (service)!!!")
        print("---- get fastapi app ------")
        print(self._app)

        self._app.state.house_price_model = HousePriceModel(DEFAULT_MODEL_PATH)

    def teardown(self):
        print("call pre teardown from EndpointHooksImpl (service)!!!")


class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self):
        super(EndpointAsyncHooksImpl, self).__init__()

    async def setup(self):
        print("call pre setup from EndpointAsyncHooksImpl (service)!!!")

    async def teardown(self):
        print("call pre teardown from EndpointAsyncHooksImpl (service)!!!")


