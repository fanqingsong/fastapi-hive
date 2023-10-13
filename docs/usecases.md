# Some frequent use cases.


## 1. Machine Learning model preloading during app startup.

---

For machine learning model, it is not suitable to load model during request, because the time of model loading may be too long, so the proposed method is to load model before request, i.e. during app startup.

For the classical code layout example, it defines loading model logic func(start_app_handler) in core.event_handler.py file.

**Reference**: <a href="https://github.com/eightBEC/fastapi-ml-skeleton/tree/master/fastapi_skeleton" target="_blank">https://github.com/eightBEC/fastapi-ml-skeleton/tree/master/fastapi_skeleton</a>


```python
from typing import Callable

from fastapi import FastAPI
from loguru import logger

from fastapi_skeleton.core.config import DEFAULT_MODEL_PATH
from fastapi_skeleton.services.models import HousePriceModel


def _startup_model(app: FastAPI) -> None:
    model_path = DEFAULT_MODEL_PATH
    model_instance = HousePriceModel(model_path)
    app.state.model = model_instance


def _shutdown_model(app: FastAPI) -> None:
    app.state.model = None


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_model(app)
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model(app)
    return shutdown
```

Then register start_app_handler as startup event in main.py, so model will be load when startup event happens.

```python
from fastapi import FastAPI

from fastapi_skeleton.api.routes.router import api_router
from fastapi_skeleton.core.config import (API_PREFIX, APP_NAME, APP_VERSION,
                                          IS_DEBUG)
from fastapi_skeleton.core.event_handlers import (start_app_handler,
                                                  stop_app_handler)


def get_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)
    fast_app.include_router(api_router, prefix=API_PREFIX)

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app


app = get_app()
```

But for the ideal code structure, we take assumption that all codes of one service should be put in one folder together. 

FastAPI hive really support this code structure, and meet the preloading requirement which is implemented by regiser startup event.

in the below file, we use setup hook to load machine learning model before request, and save loaded model as self._app.state.house_price_model.

example/endpoints_package1/house_price/service/__init__.py


```python
from example.endpoints_package1.house_price.service.implement import HousePriceModel

from example.endpoints_package1.house_price.config import DEFAULT_MODEL_PATH

from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_model import EndpointHooks, EndpointAsyncHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self, app: FastAPI):
        super(EndpointHooksImpl, self).__init__(app)

    def setup(self):
        print("call pre setup from EndpointHooksImpl (service)!!!")
        print("---- get fastapi app ------")
        print(self._app)

        self._app.state.house_price_model = HousePriceModel(DEFAULT_MODEL_PATH)

    def teardown(self):
        print("call pre teardown from EndpointHooksImpl (service)!!!")


class EndpointAsyncHooksImpl(EndpointAsyncHooks):

    def __init__(self, app: FastAPI):
        super(EndpointAsyncHooksImpl, self).__init__(app)

    async def setup(self):
        print("call pre setup from EndpointAsyncHooksImpl (service)!!!")

    async def teardown(self):
        print("call pre teardown from EndpointAsyncHooksImpl (service)!!!")


```

Then in router file, we implement predict endpoint which call loaded model with variable request.app.state.house_price_model

example/endpoints_package1/house_price/router/implement.py

```python
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

    model: HousePriceModel = request.app.state.house_price_model
    prediction: HousePredictionResult = model.predict(block_data)

    return prediction

```

---


## DB ORM definition and table creation.

---

TBA

