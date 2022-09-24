
from fastapi_modules.modules_another.house_price_another.service.implement import HousePriceModel

model_path = "./fastapi_modules/modules_another/house_price_another/model/lin_reg_california_housing_model.joblib"

service = HousePriceModel(model_path)
