

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer


class EndpointContainerMounter:
    @inject
    def __init__(
            self,
            app: FastAPI,
            endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container]
    ) -> None:
        logger.info("endpoint container mounter is starting.")

        self._app = app
        self._endpoint_container = endpoint_container

    def mount(self) -> None:
        app: FastAPI = self._app
        app.state.endpoint_container = self._endpoint_container

    def unmount(self) -> None:
        app: FastAPI = self._app
        app.state.endpoint_container = None
