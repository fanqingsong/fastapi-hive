
from fastapi import FastAPI
from fastapi_modules.core.config import (API_PREFIX)
from typing import Callable, Dict
from loguru import logger
from fastapi_modules.ioc_container.router_mounter import router_mounter
from fastapi_modules.ioc_container.module_mounter import module_mounter


class IoCContainer:
    def __init__(self):
        self._app = None
        self._params = {
            "API_PREFIX": ""
        }

    def bind_app(self, app: FastAPI):
        self._app = app

        return self

    def set_params(self, params: Dict):
        self._params.update(params)

        return self

    def _setup(self) -> None:
        module_mounter.mount()
        router_mounter.mount(self._params.get("API_PREFIX"))

    def _teardown(self) -> None:
        module_mounter.unmount()
        module_mounter.unmount()

    def _start_container_handler(self) -> Callable:
        def startup() -> None:
            logger.info("Running container start handler.")

            self._setup()
        return startup

    def _stop_container_handler(self) -> Callable:
        def shutdown() -> None:
            logger.info("Running container shutdown handler.")

            self._teardown()
        return shutdown

    def init(self) -> None:
        app = self._app
        module_mounter.bind_app(app)
        router_mounter.bind_app(app)

        app.add_event_handler("startup", self._start_container_handler())
        app.add_event_handler("shutdown", self._stop_container_handler())

