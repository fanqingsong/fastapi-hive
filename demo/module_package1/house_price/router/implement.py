from fastapi import APIRouter, Depends
from starlette.requests import Request

from demo.core import security

from demo.module_package1.house_price.schema.payload import (
    HousePredictionPayload)
from demo.module_package1.house_price.schema.prediction import HousePredictionResult

from demo.module_package1.house_price.service import HousePriceModel

from fastapi_modules.ioc_framework.module_container import ModuleContainer

router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    module_container: ModuleContainer = request.app.state.module_container
    model: HousePriceModel = module_container.get_module("house_price").service
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
