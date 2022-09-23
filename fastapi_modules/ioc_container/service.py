

from typing import Callable

from fastapi import FastAPI
from loguru import logger
from fastapi_modules.ioc_container.discover import discover


def setup_service(app: FastAPI) -> None:
    app.state.discover = discover


def teardown_service(app: FastAPI) -> None:
    app.state.discover = None

