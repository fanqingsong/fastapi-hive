from fastapi import APIRouter, Depends
from starlette.requests import Request

from demo.cornerstone import security

from demo.xxx_endpoint.house_price.schema.payload import (
    HousePredictionPayload)
from demo.xxx_endpoint.house_price.schema.prediction import HousePredictionResult

from demo.xxx_endpoint.house_price.service import HousePriceModel

from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer

router = APIRouter()


@router.post("/predict", response_model=HousePredictionResult, name="predict")
def post_predict(
    request: Request,
    authenticated: bool = Depends(security.validate_request),
    block_data: HousePredictionPayload = None
) -> HousePredictionResult:

    module_container: EndpointContainer = request.app.state.endpoint_container
    model: HousePriceModel = module_container.get_endpoint("house_price").service
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction
