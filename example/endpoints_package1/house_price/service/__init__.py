

from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.decorators import endpoint, provides


@endpoint(name="house_price")
class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    @provides(HousePriceModel)
    def startup(self):
        print("call pre startup from EndpointHooksImpl (service)!!!")

        return HousePriceModel(DEFAULT_MODEL_PATH)

    def shutdown(self):
        print("call pre shutdown from EndpointHooksImpl (service)!!!")
