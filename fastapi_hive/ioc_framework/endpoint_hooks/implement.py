from typing import Callable
from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer, EndpointMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi import APIRouter, FastAPI
from typing import Optional
from abc import ABC, abstractmethod


class EndpointHooks(ABC):
    '''
    Base class for EndpointHooks cornerstones.

    Usage
    ===

    In your EndpointHooks cornerstones `__init__.py` create a subclass of `EndpointHooks`

    ```python
    from fastapi_hive.ioc_framework.endpoint_model import EndpointHooks


    class EndpointHooksImpl(EndpointHooks):
        def setup(self):
            pass
    ```
    '''

    def __init__(self) -> None:
        self._app: Optional[FastAPI] = None
        self._endpoint: Optional[EndpointMeta] = None
        self._app_state: Optional[dict] = None

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value: FastAPI):
        self._app = value

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: EndpointMeta):
        self._endpoint = value

    @property
    def app_state(self):
        return self._app_state

    @app_state.setter
    def app_state(self, value: dict):
        self._app_state = value

    def setup(self):
        pass

    def teardown(self):
        pass


class EndpointAsyncHooks(ABC):
    '''
    Base class for EndpointHooks cornerstones in async mode.

    Usage
    ===

    In your EndpointHooks cornerstones `__init__.py` create a subclass of `EndpointAsyncHooks`

    ```python
    from fastapi_hive.ioc_framework.endpoint_model import EndpointAsyncHooks


    class EndpointAsyncHooksImpl(EndpointAsyncHooks):
        async def setup(self):
            pass
    ```
    '''

    def __init__(self) -> None:
        self._app: Optional[FastAPI] = None
        self._endpoint: Optional[EndpointMeta] = None
        self._app_state: Optional[dict] = None

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value: FastAPI):
        self._app = value

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, value: EndpointMeta):
        self._endpoint = value

    @property
    def app_state(self):
        return self._app_state

    @app_state.setter
    def app_state(self, value: dict):
        self._app_state = value

    async def setup(self):
        pass

    async def teardown(self):
        pass


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
        def callback_iter(one_endpoint: EndpointMeta):
            imported_module_db = one_endpoint.imported_module_db
            self._exec_callback_if_possible(imported_module_db, callback, one_endpoint)

            imported_module_router = one_endpoint.imported_module_router
            self._exec_callback_if_possible(imported_module_router, callback, one_endpoint)

            imported_module_service = one_endpoint.imported_module_service
            self._exec_callback_if_possible(imported_module_service, callback, one_endpoint)

            imported_module = one_endpoint.imported_module
            self._exec_callback_if_possible(imported_module, callback, one_endpoint)

        self._endpoint_container.iterate_endpoints(callback_iter)

    def _exec_callback_if_possible(self, imported_module, callback: Callable, one_endpoint: EndpointMeta):
        if not hasattr(imported_module, 'EndpointHooksImpl'):
            return

        app: FastAPI = self._app

        endpoint_hooks: EndpointHooks = imported_module.EndpointHooksImpl()

        endpoint_hooks.app = app
        endpoint_hooks.endpoint = one_endpoint

        pkg_path = f'{one_endpoint.container_name}.{one_endpoint.name}'
        endpoint_hooks.app_state = app.state.endpoints[pkg_path]

        callback(endpoint_hooks)

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
        async def callback_iter(one_endpoint: EndpointMeta):
            imported_module_db = one_endpoint.imported_module_db
            await self._exec_callback_if_possible(imported_module_db, callback, one_endpoint)

            imported_module_router = one_endpoint.imported_module_router
            await self._exec_callback_if_possible(imported_module_router, callback, one_endpoint)

            imported_module_service = one_endpoint.imported_module_service
            await self._exec_callback_if_possible(imported_module_service, callback, one_endpoint)

            imported_module = one_endpoint.imported_module
            await self._exec_callback_if_possible(imported_module, callback, one_endpoint)

        await self._endpoint_container.async_iterate_endpoints(callback_iter)

    async def _exec_callback_if_possible(self, imported_module, callback: Callable, one_endpoint: EndpointMeta):
        if not hasattr(imported_module, 'EndpointAsyncHooksImpl'):
            return

        app = self._app

        endpoint_hooks: EndpointAsyncHooks = imported_module.EndpointAsyncHooksImpl()

        endpoint_hooks.app = app
        endpoint_hooks.endpoint = one_endpoint

        pkg_path = f'{one_endpoint.container_name}.{one_endpoint.name}'
        endpoint_hooks.app_state = app.state.endpoints[pkg_path]

        await callback(endpoint_hooks)

    async def run_setup_hook(self):
        async def callback(endpoint: EndpointAsyncHooks):
            await endpoint.setup()

        await self._iterate_endpoints(callback)

    async def run_teardown_hook(self):
        async def callback(endpoint: EndpointAsyncHooks):
            await endpoint.teardown()

        await self._iterate_endpoints(callback)


