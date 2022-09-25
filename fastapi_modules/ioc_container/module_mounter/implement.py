

from fastapi import FastAPI
from loguru import logger
from fastapi_modules.ioc_container.module_container import module_container


class ModuleMounter:
    def __int__(self) -> None:
        logger.info("module mounter is starting.")

        self._app = None

    def bind_app(self, app: FastAPI):
        self._app = app

    def mount(self) -> None:
        app: FastAPI = self._app
        app.state.module_container = module_container

    def unmount(self) -> None:
        app: FastAPI = self._app
        app.state.module_container = None
