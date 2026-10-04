
from example.endpoints_package2.house_price2.service.implement import HousePriceModel

from example.endpoints_package2.house_price2.config import DEFAULT_MODEL_PATH

from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks, EndpointAsyncHooks
from fastapi_hive.ioc_framework.decorators import endpoint, provides


@endpoint(name="house_price2")
class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    @provides(HousePriceModel)
    def setup(self):
        print("call pre setup from EndpointHooksImpl (service)!!!")
        print("---- get fastapi app ------")
        print(self.app)

        return HousePriceModel(DEFAULT_MODEL_PATH)

    def teardown(self):
        print("call pre teardown from EndpointHooksImpl (service)!!!")


@endpoint(name="house_price2")
class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self):
        super(EndpointAsyncHooksImpl, self).__init__()

    async def setup(self):
        print("call pre setup from EndpointAsyncHooksImpl (service)!!!")

    async def teardown(self):
        print("call pre teardown from EndpointAsyncHooksImpl (service)!!!")

