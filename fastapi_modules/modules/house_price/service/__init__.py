
from fastapi_modules.modules.house_price.service.implement import HousePriceModel

model_path = "./fastapi_modules/modules/house_price/model/lin_reg_california_housing_model.joblib"

service = HousePriceModel(model_path)
