from fastapi import APIRouter

from fastapi_hive.ioc_framework.registry import Inject

from example.endpoints_package1.house_price.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package1.house_price.schema.prediction import HousePredictionResult

from example.endpoints_package1.house_price.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    model: HousePriceModel = Inject(HousePriceModel),
    authenticated: bool = Inject("auth.ok"),
    block_data: HousePredictionPayload = None,
) -> HousePredictionResult:

    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
