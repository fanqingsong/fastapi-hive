

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from fastapi_hive.ioc_framework.endpoint_model import Endpoint, EndpointAsync, EndpointMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


class EndpointHookCaller:
    @inject
    def __init__(
            self,
            app: FastAPI,
            endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("endpoint hook caller is starting.")

        self._app = app
        self._endpoint_container = endpoint_container
        self._ioc_config = ioc_config

    def run_setup_hook(self):

        modules = self._endpoint_container.modules
        for one_module, one_entity in modules.items():
            one_entity: EndpointMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'EndpointImpl'):
                continue

            endpoint: Endpoint = imported_module.EndpointImpl(self._app)

            endpoint.setup()

    def run_teardown_hook(self):
        modules = self._endpoint_container.modules
        for one_module, one_entity in modules.items():
            one_entity: EndpointMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'EndpointImpl'):
                continue

            cornerstone: Endpoint = imported_module.EndpointImpl(self._app)

            cornerstone.teardown()


class EndpointHookAsyncCaller:
    @inject
    def __init__(
            self,
            app: FastAPI,
            endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("endpoint hook async caller is starting.")

        self._app = app
        self._endpoint_container = endpoint_container
        self._ioc_config = ioc_config

    async def run_setup_hook(self):
        modules = self._endpoint_container.modules
        for one_module, one_entity in modules.items():
            one_entity: EndpointMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'EndpointAsyncImpl'):
                continue

            endpoint: EndpointAsync = imported_module.EndpointAsyncImpl(self._app)

            await endpoint.setup()

    async def run_teardown_hook(self):
        modules = self._endpoint_container.modules
        for one_module, one_entity in modules.items():
            one_entity: EndpointMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'EndpointAsyncImpl'):
                continue

            endpoint: EndpointAsync = imported_module.EndpointAsyncImpl(self._app)

            await endpoint.teardown()

