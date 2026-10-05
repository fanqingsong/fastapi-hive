from example.endpoints_package2.house_price2.service.implement import HousePriceModel
from example.endpoints_package2.house_price2.config import DEFAULT_MODEL_PATH
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.decorators import endpoint, provides


@endpoint(name="house_price2")
class EndpointHooksImpl(EndpointHooks):

    @provides(HousePriceModel)
    def model(self):
        return HousePriceModel(DEFAULT_MODEL_PATH)
