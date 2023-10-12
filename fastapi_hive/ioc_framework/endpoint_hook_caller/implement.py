from typing import Callable

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from fastapi_hive.ioc_framework.endpoint_model import EndpointHooks, EndpointAsyncHooks, EndpointMeta
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
        logger.info("endpoint hook caller is initializing.")

        self._app = app
        self._endpoint_container = endpoint_container
        self._ioc_config = ioc_config

    def _iterate_endpoints(self, callback: Callable):
        endpoints = self._endpoint_container.endpoints
        for _, one_endpoint in endpoints.items():
            one_endpoint: EndpointMeta = one_endpoint

            imported_module_db = one_endpoint.imported_module_db
            self._exec_callback_if_possible(imported_module_db, callback)

            imported_module_router = one_endpoint.imported_module_router
            self._exec_callback_if_possible(imported_module_router, callback)

            imported_module_service = one_endpoint.imported_module_service
            self._exec_callback_if_possible(imported_module_service, callback)

            imported_module = one_endpoint.imported_module
            self._exec_callback_if_possible(imported_module, callback)

    def _exec_callback_if_possible(self, imported_module, callback: Callable):
        if not hasattr(imported_module, 'EndpointHooksImpl'):
            return

        endpoint: EndpointHooks = imported_module.EndpointHooksImpl(self._app)

        callback(endpoint)

    def run_setup_hook(self):
        def callback(endpoint: EndpointHooks):
            endpoint.setup()

        self._iterate_endpoints(callback)

    def run_teardown_hook(self):
        def callback(endpoint: EndpointHooks):
            endpoint.teardown()

        self._iterate_endpoints(callback)


class EndpointHookAsyncCaller:
    @inject
    def __init__(
            self,
            app: FastAPI,
            endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("endpoint hook async caller is initializing.")

        self._app = app
        self._endpoint_container = endpoint_container
        self._ioc_config = ioc_config

    async def _iterate_endpoints(self, callback: Callable):
        endpoints = self._endpoint_container.endpoints
        for _, one_endpoint in endpoints.items():
            one_endpoint: EndpointMeta = one_endpoint

            imported_module_db = one_endpoint.imported_module_db
            await self._exec_callback_if_possible(imported_module_db, callback)

            imported_module_router = one_endpoint.imported_module_router
            await self._exec_callback_if_possible(imported_module_router, callback)

            imported_module_service = one_endpoint.imported_module_service
            await self._exec_callback_if_possible(imported_module_service, callback)

            imported_module = one_endpoint.imported_module
            await self._exec_callback_if_possible(imported_module, callback)

    async def _exec_callback_if_possible(self, imported_module, callback: Callable):
        if not hasattr(imported_module, 'EndpointAsyncHooksImpl'):
            return

        endpoint: EndpointAsyncHooks = imported_module.EndpointAsyncHooksImpl(self._app)

        await callback(endpoint)

    async def run_setup_hook(self):
        async def callback(endpoint: EndpointHooks):
            await endpoint.setup()

        await self._iterate_endpoints(callback)

    async def run_teardown_hook(self):
        async def callback(endpoint: EndpointHooks):
            await endpoint.teardown()

        await self._iterate_endpoints(callback)


