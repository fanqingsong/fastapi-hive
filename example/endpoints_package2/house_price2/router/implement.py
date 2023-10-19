from fastapi import APIRouter, Depends
from starlette.requests import Request

from example.cornerstone import auth

from example.endpoints_package2.house_price2.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package2.house_price2.schema.prediction import HousePredictionResult

from example.endpoints_package2.house_price2.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict2")
def post_predict(
    request: Request,
    authenticated: bool = Depends(auth.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    model: HousePriceModel = request.app.state.endpoints['endpoints_package2.house_price2']['service']
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
