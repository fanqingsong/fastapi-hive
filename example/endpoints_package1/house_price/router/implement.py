from fastapi import APIRouter, Depends

from example.cornerstone import auth
from fastapi_hive.ioc_framework.registry import DependsHive

from example.endpoints_package1.house_price.schema.payload import (
    HousePredictionPayload)
from example.endpoints_package1.house_price.schema.prediction import HousePredictionResult

from example.endpoints_package1.house_price.service import HousePriceModel


router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    authenticated: bool = Depends(auth.validate_request),
    block_data: HousePredictionPayload = None,
    model: HousePriceModel = DependsHive(HousePriceModel),
) -> HousePredictionResult:

    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
