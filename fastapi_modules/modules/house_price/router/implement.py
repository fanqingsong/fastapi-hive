from fastapi import APIRouter, Depends
from starlette.requests import Request

from fastapi_modules.core import security

from fastapi_modules.modules.house_price.schema.payload import (
    HousePredictionPayload, payload_to_list)
from fastapi_modules.modules.house_price.schema.prediction import HousePredictionResult

from fastapi_modules.modules.house_price.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    model: HousePriceModel = request.app.state.discover.get_module("house_price").service
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
