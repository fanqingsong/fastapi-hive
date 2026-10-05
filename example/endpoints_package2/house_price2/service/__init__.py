from example.endpoints_package2.house_price2.service.implement import HousePriceModel
from example.endpoints_package2.house_price2.config import DEFAULT_MODEL_PATH
from fastapi_hive.ioc_framework.decorators import autoconfigure, provides


@autoconfigure(name="house_price2.model")
class HousePriceModelAuto:

    @provides(HousePriceModel)
    def model(self):
        return HousePriceModel(DEFAULT_MODEL_PATH)
