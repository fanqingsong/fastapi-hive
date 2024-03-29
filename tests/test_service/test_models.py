
import pytest

from example.endpoints_package1.house_price.schema.payload import HousePredictionPayload
from example.endpoints_package1.house_price.schema.prediction import HousePredictionResult
from example.endpoints_package1.house_price.service.implement import HousePriceModel
from example.endpoints_package1.house_price import config


def test_prediction(test_client) -> None:
    model_path = config.DEFAULT_MODEL_PATH
    hpp = HousePredictionPayload.parse_obj({
        "median_income_in_block": 8.3252,
        "median_house_age_in_block": 41,
        "average_rooms": 6,
        "average_bedrooms": 1,
        "population_per_block": 322,
        "average_house_occupancy": 2.55,
        "block_latitude": 37.88,
        "block_longitude": -122.23
    })

    hpm = HousePriceModel(model_path)
    result = hpm.predict(hpp)
    assert isinstance(result, HousePredictionResult)


def test_prediction_no_payload(test_client) -> None:
    model_path = config.DEFAULT_MODEL_PATH

    hpm = HousePriceModel(model_path)
    with pytest.raises(ValueError):
        result = hpm.predict(None)
        assert isinstance(result, HousePredictionResult)
