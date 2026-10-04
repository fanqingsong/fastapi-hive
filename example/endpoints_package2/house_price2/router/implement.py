from fastapi import APIRouter, Depends

from example.cornerstone import auth
from fastapi_hive.ioc_framework.registry import DependsHive

from example.endpoints_package2.house_price2.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package2.house_price2.schema.prediction import HousePredictionResult

from example.endpoints_package2.house_price2.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict2")
def post_predict(
    authenticated: bool = Depends(auth.validate_request),
    block_data: HousePredictionPayload = None,
    model: HousePriceModel = DependsHive(HousePriceModel),
) -> HousePredictionResult:

    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
