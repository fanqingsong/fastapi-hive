from fastapi import APIRouter, Depends
from starlette.requests import Request

from demo.cornerstone import security

from demo.yyy_endpoint.house_price2.schema.payload import (
    HousePredictionPayload)
from demo.yyy_endpoint.house_price2.schema.prediction import HousePredictionResult

from demo.yyy_endpoint.house_price2.service import HousePriceModel, service


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    model: HousePriceModel = service
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
