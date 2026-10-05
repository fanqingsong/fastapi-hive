from typing import Optional
from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer, CornerstoneMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi import FastAPI
from abc import ABC
from starlette.requests import Request
from fastapi_hive.ioc_framework.decorators import bind_cornerstone, create_hook, invoke, invoke_sync, select_hooks


class CornerstoneHooks(ABC):
    '''
    Base class for cornerstone hooks.

    Usage
    ===

    In your cornerstone `__init__.py` create a subclass of `CornerstoneHooks`

    ```python
    from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks


    class CornerstoneImpl(CornerstoneHooks):
        def configure(self):
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

    def configure(self):
        """Assemble-time only. Register middleware. Must not be async."""
        pass

    def pre_endpoint_startup(self):
        """应用启动时、各 endpoint 执行 startup 之前调用。"""
        pass

    def post_endpoint_startup(self):
        """应用启动时、各 endpoint 执行 startup 之后调用。"""
        pass

    def pre_endpoint_shutdown(self):
        """应用关闭时、各 endpoint 执行 shutdown 之前调用。"""
        pass

    def post_endpoint_shutdown(self):
        """应用关闭时、各 endpoint 执行 shutdown 之后调用。"""
        pass

    def pre_endpoint_call(self):
        """每次 HTTP 请求进入 endpoint 处理逻辑之前调用。"""
        pass

    def post_endpoint_call(self):
        """每次 HTTP 请求完成 endpoint 处理逻辑之后调用。"""
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
            for cls in meta.hooks:
                pairs.append((cls, meta))
        return select_hooks(pairs, self._ioc_config)

    def _bind(self, cls, meta, request: Request = None):
        app_registry = getattr(self._app.state, "hive", None)
        instance = create_hook(cls, app_registry)
        bind_cornerstone(instance, self._app, meta, request)
        return instance, app_registry

    def run_configure(self):
        logger.info("running cornerstone_hooks configure...")
        for cls, meta in self._pairs():
            instance, app_registry = self._bind(cls, meta)
            invoke_sync(instance, "configure", app_registry)

    async def _run(self, method_name: str, request: Request = None):
        app_registry = getattr(self._app.state, "hive", None)
        request_registry = getattr(request.state, "hive", None) if request is not None else None
        for cls, meta in self._pairs():
            instance, _ = self._bind(cls, meta, request)
            await invoke(instance, method_name, app_registry, request_registry)

    async def run_pre_startup_hook(self):
        logger.info("running cornerstone_hooks pre endpoint startup...")
        await self._run("pre_endpoint_startup")

    async def run_post_startup_hook(self):
        logger.info("running cornerstone_hooks post endpoint startup...")
        await self._run("post_endpoint_startup")

    async def run_pre_shutdown_hook(self):
        logger.info("running cornerstone_hooks pre endpoint shutdown...")
        await self._run("pre_endpoint_shutdown")

    async def run_post_shutdown_hook(self):
        logger.info("running cornerstone_hooks post endpoint shutdown...")
        await self._run("post_endpoint_shutdown")

    async def run_pre_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks pre endpoint call...")
        await self._run("pre_endpoint_call", request)

    async def run_post_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks post endpoint call...")
        await self._run("post_endpoint_call", request)
