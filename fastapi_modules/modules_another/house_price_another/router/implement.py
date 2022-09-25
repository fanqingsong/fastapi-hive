from fastapi import APIRouter, Depends
from starlette.requests import Request

from fastapi_modules.core import security

from fastapi_modules.modules_another.house_price_another.schema.payload import (
    HousePredictionPayload)
from fastapi_modules.modules_another.house_price_another.schema.prediction import HousePredictionResult

from fastapi_modules.modules_another.house_price_another.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    model: HousePriceModel = request.app.state.module_container.get_module(
        "house_price_another").service
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
