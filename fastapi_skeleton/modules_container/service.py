

from typing import Callable

from fastapi import FastAPI
from loguru import logger
from fastapi_skeleton.modules_container.discover import discover


def _startup_service(app: FastAPI) -> None:
    app.state.discover = discover


def _shutdown_service(app: FastAPI) -> None:
    app.state.discover = None


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        _startup_service(app)
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_service(app)
    return shutdown
