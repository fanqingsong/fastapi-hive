from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer, EndpointMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from typing import Optional
from abc import ABC
from fastapi_hive.ioc_framework.decorators import bind_endpoint, create_hook, invoke, select_hooks


class EndpointHooks(ABC):
    '''
    Base class for EndpointHooks.

    Usage
    ===

    In your endpoint `__init__.py` create a subclass of `EndpointHooks`

    ```python
    from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


    class EndpointHooksImpl(EndpointHooks):
        def startup(self):
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

    def startup(self):
        pass

    def shutdown(self):
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

    def _pairs(self):
        pairs = []
        for meta in self._endpoint_container.endpoints.values():
            for cls in meta.hooks:
                pairs.append((cls, meta))
        return select_hooks(pairs, self._ioc_config)

    async def _run(self, method_name: str):
        app_registry = getattr(self._app.state, "hive", None)
        for cls, meta in self._pairs():
            instance = create_hook(cls, app_registry)
            bind_endpoint(instance, self._app, meta)
            await invoke(instance, method_name, app_registry)

    async def run_startup_hook(self):
        await self._run("startup")

    async def run_shutdown_hook(self):
        await self._run("shutdown")
