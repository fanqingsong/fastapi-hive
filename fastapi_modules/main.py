

from fastapi import FastAPI
from typing import Callable
from loguru import logger
from fastapi_modules.core.config import (APP_NAME, APP_VERSION,
                                         IS_DEBUG)

from fastapi_modules.ioc_container import (setup, teardown)


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")

        setup(app)
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")

        teardown(app)
    return shutdown


def get_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app


app = get_app()
