from fastapi import APIRouter, Depends
from starlette.requests import Request

from demo.core import security

from demo.package2.house_price2.schema.payload import (
    HousePredictionPayload)
from demo.package2.house_price2.schema.prediction import HousePredictionResult

from demo.package2.house_price2.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    model: HousePriceModel = request.app.state.module_container.get_module(
        "house_price2").service
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
