
from fastapi_skeleton.modules.house_price.service.implement import HousePriceModel

model_path = "./fastapi_skeleton/modules/house_price/model/lin_reg_california_housing_model.joblib"

model_instance = HousePriceModel(model_path)

