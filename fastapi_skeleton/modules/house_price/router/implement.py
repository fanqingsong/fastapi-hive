from fastapi import APIRouter, Depends
from starlette.requests import Request

from fastapi_skeleton.core import security

from fastapi_skeleton.modules.house_price.pydantic_model.payload import (HousePredictionPayload, payload_to_list)
from fastapi_skeleton.modules.house_price.pydantic_model.prediction import HousePredictionResult

from fastapi_skeleton.modules.house_price.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    model: HousePriceModel = request.app.state.discover.get_module("house_price")["service"].model_instance
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
