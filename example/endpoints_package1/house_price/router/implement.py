from fastapi import APIRouter, Depends
from starlette.requests import Request

from example.cornerstone import auth

from example.endpoints_package1.house_price.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package1.house_price.schema.prediction import HousePredictionResult

from example.endpoints_package1.house_price.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(auth.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    model: HousePriceModel = request.app.state.endpoints['endpoints_package1.house_price']['house_price_model']
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
