from fastapi import APIRouter, Depends
from starlette.requests import Request

from example.cornerstone import security

from example.endpoints_package2.house_price2.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package2.house_price2.schema.prediction import HousePredictionResult

from example.endpoints_package2.house_price2.service import HousePriceModel, get_service


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    service = get_service()
    model: HousePriceModel = service
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
