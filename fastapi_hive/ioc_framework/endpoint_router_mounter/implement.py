

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from fastapi_hive.ioc_framework.endpoint_model import Endpoint
from fastapi import APIRouter
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


__all__ = ["EndpointRouterMounter"]


class EndpointRouterMounter:
    @inject
    def __init__(
            self,
            app: FastAPI,
            endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("endpoint router mounter is starting.")

        self._app = app
        self._endpoint_container = endpoint_container
        self._ioc_config = ioc_config

        # print("-------------_endpoint_container in  EndpointRouterMounter init------------------")
        # print(dir(self._endpoint_container))

    def mount(self, api_prefix: str) -> None:
        app: FastAPI = self._app

        api_router = self._collect_router()
        app.include_router(api_router, prefix=api_prefix)

    def _collect_router(self) -> APIRouter:
        api_router = APIRouter()

        hide_package = self._ioc_config.HIDE_PACKAGE_IN_URL

        modules = self._endpoint_container.modules
        #
        # print("-------------------------------")
        # print(dir(self._endpoint_container))

        for one_module, one_entity in modules.items():
            one_entity: Endpoint = one_entity
            module_router = one_entity.router
            package_name = one_entity.package

            prefix = f"/{package_name}/{one_module}"
            if hide_package:
                prefix = f"/{one_module}"

            '''
            set package in url
            '''
            api_router.include_router(
                module_router,
                tags=[f"{package_name}.{one_module}"],
                prefix=prefix)

        return api_router

    def unmount(self, api_prefix: str) -> None:
        pass
        # app: FastAPI = self._app

        '''
        fastapi don't support unmount router now.
        '''
        # api_router = APIRouter()
        # app.include_router(api_router, prefix=api_prefix)
