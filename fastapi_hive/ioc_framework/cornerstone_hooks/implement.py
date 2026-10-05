from typing import Optional
from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer, CornerstoneMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi import FastAPI
from abc import ABC
from starlette.requests import Request
from fastapi_hive.ioc_framework.decorators import bind_cornerstone, create_hook, invoke, invoke_async, select_hooks


class CornerstoneHooks(ABC):
    '''
    Base class for cornerstone hooks.

    Usage
    ===

    In your cornerstone cornerstones `__init__.py` create a subclass of `CornerstoneHooks`

    ```python
    from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneHooks


    class CornerstoneImpl(CornerstoneHooks):
        def pre_endpoint_startup(self):
            pass
    ```
    '''

    def __init__(self) -> None:
        self._app: Optional[FastAPI] = None
        self._cornerstone: Optional[CornerstoneMeta] = None
        self._request: Optional[Request] = None
        self._app_state: Optional[dict] = None
        self._request_state: Optional[dict] = None

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value: FastAPI):
        self._app = value

    @property
    def cornerstone(self):
        return self._cornerstone

    @cornerstone.setter
    def cornerstone(self, value: CornerstoneMeta):
        self._cornerstone = value

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, value: Request):
        self._request = value

    @property
    def app_state(self):
        return self._app_state

    @app_state.setter
    def app_state(self, value: dict):
        self._app_state = value

    @property
    def request_state(self):
        return self._request_state

    @request_state.setter
    def request_state(self, value: dict):
        self._request_state = value

    def pre_endpoint_startup(self):
        pass

    def post_endpoint_startup(self):
        pass

    def pre_endpoint_shutdown(self):
        pass

    def post_endpoint_shutdown(self):
        pass

    def pre_endpoint_call(self):
        pass

    def post_endpoint_call(self):
        pass


class CornerstoneAsyncHooks(ABC):
    '''
    Base class for cornerstone cornerstones in async mode.

    Usage
    ===

    In your cornerstone cornerstones `__init__.py` create a subclass of `CornerstoneAsyncHooks`

    ```python
    from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneAsyncHooks


    class CornerstoneAsyncImpl(CornerstoneAsyncHooks):
        async def pre_endpoint_startup(self):
            pass
    ```
    '''

    def __init__(self) -> None:
        self._app: Optional[FastAPI] = None
        self._cornerstone: Optional[CornerstoneMeta] = None
        self._request: Optional[Request] = None
        self._app_state: Optional[dict] = None
        self._req_state: Optional[dict] = None

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value: FastAPI):
        self._app = value

    @property
    def cornerstone(self):
        return self._cornerstone

    @cornerstone.setter
    def cornerstone(self, value: CornerstoneMeta):
        self._cornerstone = value

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, value: Request):
        self._request = value

    @property
    def app_state(self):
        return self._app_state

    @app_state.setter
    def app_state(self, value: dict):
        self._app_state = value

    @property
    def req_state(self):
        return self._req_state

    @req_state.setter
    def req_state(self, value: dict):
        self._req_state = value

    async def pre_endpoint_startup(self):
        pass

    async def post_endpoint_startup(self):
        pass

    async def pre_endpoint_shutdown(self):
        pass

    async def post_endpoint_shutdown(self):
        pass

    async def pre_endpoint_call(self):
        pass

    async def post_endpoint_call(self):
        pass


class CornerstoneHookCaller:
    @inject
    def __init__(
            self,
            app: FastAPI,
            cornerstone_container: CornerstoneContainer = Provide[DIContainer.cornerstone_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("conerstone hook caller is initializing.")

        self._app = app
        self._cornerstone_container = cornerstone_container
        self._ioc_config = ioc_config

    def _pairs(self):
        pairs = []
        for meta in self._cornerstone_container.cornerstones.values():
            for cls in meta.sync_hooks:
                pairs.append((cls, meta))
        return select_hooks(pairs, self._ioc_config)

    def _run(self, method_name: str, request: Request = None):
        app_registry = getattr(self._app.state, "hive", None)
        request_registry = getattr(request.state, "hive", None) if request is not None else None
        for cls, meta in self._pairs():
            instance = create_hook(cls, app_registry)
            bind_cornerstone(instance, self._app, meta, request)
            invoke(instance, method_name, app_registry, request_registry)

    def run_pre_startup_hook(self):
        logger.info("running cornerstone_hooks sync pre endpoint startup...")
        self._run("pre_endpoint_startup")

    def run_post_startup_hook(self):
        logger.info("running cornerstone_hooks sync post endpoint startup...")
        self._run("post_endpoint_startup")

    def run_pre_shutdown_hook(self):
        logger.info("running cornerstone_hooks sync pre endpoint shutdown...")
        self._run("pre_endpoint_shutdown")

    def run_post_shutdown_hook(self):
        logger.info("running cornerstone_hooks sync post endpoint shutdown...")
        self._run("post_endpoint_shutdown")

    def run_pre_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks sync pre endpoint call...")
        self._run("pre_endpoint_call", request)

    def run_post_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks sync post endpoint call...")
        self._run("post_endpoint_call", request)


class CornerstoneHookAsyncCaller:
    @inject
    def __init__(
            self,
            app: FastAPI,
            cornerstone_container: CornerstoneContainer = Provide[DIContainer.cornerstone_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("conerstone hook async caller is initializing.")

        self._app = app
        self._cornerstone_container = cornerstone_container
        self._ioc_config = ioc_config

    def _pairs(self):
        pairs = []
        for meta in self._cornerstone_container.cornerstones.values():
            for cls in meta.async_hooks:
                pairs.append((cls, meta))
        return select_hooks(pairs, self._ioc_config)

    async def _run(self, method_name: str, request: Request = None):
        app_registry = getattr(self._app.state, "hive", None)
        request_registry = getattr(request.state, "hive", None) if request is not None else None
        for cls, meta in self._pairs():
            instance = create_hook(cls, app_registry)
            bind_cornerstone(instance, self._app, meta, request)
            await invoke_async(instance, method_name, app_registry, request_registry)

    async def run_pre_startup_hook(self):
        logger.info("running cornerstone_hooks async pre endpoint startup...")
        await self._run("pre_endpoint_startup")

    async def run_post_startup_hook(self):
        logger.info("running cornerstone_hooks async post endpoint startup...")
        await self._run("post_endpoint_startup")

    async def run_pre_shutdown_hook(self):
        logger.info("running cornerstone_hooks async pre endpoint shutdown...")
        await self._run("pre_endpoint_shutdown")

    async def run_post_shutdown_hook(self):
        logger.info("running cornerstone_hooks async post endpoint shutdown...")
        await self._run("post_endpoint_shutdown")

    async def run_pre_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks async pre endpoint call...")
        await self._run("pre_endpoint_call", request)

    async def run_post_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks async post endpoint call...")
        await self._run("post_endpoint_call", request)
