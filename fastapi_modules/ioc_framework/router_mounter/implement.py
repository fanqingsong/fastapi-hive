

from fastapi import FastAPI
from loguru import logger
from fastapi_modules.ioc_framework.module_container import ModuleContainer
from fastapi_modules.ioc_framework.module_abstraction import Module
from fastapi import APIRouter
from dependency_injector.wiring import Provide, inject
from fastapi_modules.ioc_framework.di_contiainer import DIContainer


class RouterMounter:
    def __init__(
            self,
            app: FastAPI,
            module_container: ModuleContainer = Provide[DIContainer.module_container],
    ):
        logger.info("router mounter is starting.")

        self._app = app
        self._module_container = module_container

    def mount(self, api_prefix: str) -> None:
        app: FastAPI = self._app

        api_router = self._collect_router()
        app.include_router(api_router, prefix=api_prefix)

    def _collect_router(self) -> APIRouter:
        api_router = APIRouter()

        modules = self._module_container.modules
        for one_module, one_entity in modules.items():
            one_entity: Module = one_entity
            module_router = one_entity.router
            package_name = one_entity.package

            api_router.include_router(
                module_router,
                tags=[f"{package_name}"],
                prefix=f"/{one_module}")

        return api_router

    def unmount(self, api_prefix: str) -> None:
        pass
        # app: FastAPI = self._app

        '''
        fastapi don't support unmount router now.
        '''
        # api_router = APIRouter()
        # app.include_router(api_router, prefix=api_prefix)
