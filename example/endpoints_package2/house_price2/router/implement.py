from fastapi import APIRouter

from fastapi_hive.ioc_framework.registry import Inject

from example.endpoints_package2.house_price2.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package2.house_price2.schema.prediction import HousePredictionResult

from example.endpoints_package2.house_price2.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict2")
def post_predict(
    model: HousePriceModel = Inject(HousePriceModel),
    authenticated: bool = Inject("auth.ok"),
    block_data: HousePredictionPayload = None,
) -> HousePredictionResult:

    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
