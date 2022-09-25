
from fastapi_modules.modules.house_price.service.implement import HousePriceModel
from fastapi_modules.modules.house_price.config import DEFAULT_MODEL_PATH

service = HousePriceModel(DEFAULT_MODEL_PATH)
