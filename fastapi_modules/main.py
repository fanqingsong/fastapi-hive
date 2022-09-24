

from fastapi import FastAPI
from typing import Callable
from loguru import logger
from fastapi_modules.core.config import (APP_NAME, APP_VERSION, API_PREFIX,
                                         IS_DEBUG)

from fastapi_modules.ioc_container import ioc_container


def get_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    ioc_container\
        .bind_app(fast_app)\
        .set_params({"API_PREFIX": API_PREFIX})\
        .init()

    return fast_app


app = get_app()
