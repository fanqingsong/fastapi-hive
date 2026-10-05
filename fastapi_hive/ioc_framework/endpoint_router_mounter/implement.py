
from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi_hive.ioc_framework.decorators import resolve_router_target, select_routers


class EndpointRouterMounter:
    @inject
    def __init__(
            self,
            app: FastAPI,
            endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("endpoint router mounter is initializing.")

        self._app = app
        self._endpoint_container = endpoint_container
        self._ioc_config = ioc_config

    def _pairs(self):
        pairs = []
        for meta in self._endpoint_container.endpoints.values():
            for binding in meta.routers:
                pairs.append((binding, meta))
        return select_routers(pairs)

    def mount(self) -> None:
        logger.info("running endpoint router mounter.")

        app: FastAPI = self._app
        for binding, meta in self._pairs():
            logger.info(f"router mounting, endpoint name = {meta.container_name}.{meta.name}")
            prefix, tags = resolve_router_target(meta, binding, self._ioc_config)
            app.include_router(binding.router, tags=tags, prefix=prefix)
