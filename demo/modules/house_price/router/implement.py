from fastapi import APIRouter, Depends
from starlette.requests import Request

from demo.core import security

from demo.modules.house_price.schema.payload import (
    HousePredictionPayload)
from demo.modules.house_price.schema.prediction import HousePredictionResult

from demo.modules.house_price.service import HousePriceModel


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
