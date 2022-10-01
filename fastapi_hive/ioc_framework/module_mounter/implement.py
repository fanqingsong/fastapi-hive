

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.module_container import ModuleContainer
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer


class ModuleMounter:
    @inject
    def __init__(
            self,
            app: FastAPI,
            module_container: ModuleContainer = Provide[DIContainer.module_container]
    ) -> None:
        logger.info("module mounter is starting.")

        self._app = app
        self._module_container = module_container

    def mount(self) -> None:
        app: FastAPI = self._app
        app.state.module_container = self._module_container

    def unmount(self) -> None:
        app: FastAPI = self._app
        app.state.module_container = None
