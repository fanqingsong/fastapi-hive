from typing import Optional
from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer, CornerstoneMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi import FastAPI
from abc import ABC
from fastapi_hive.ioc_framework.decorators import (
    bind_cornerstone,
    create_hook,
    invoke,
    invoke_sync,
    select_hooks,
)


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

    def configure(self):
        """Assemble-time only. Register middleware. Must not be async."""
        pass

    def before_endpoint_startup(self):
        """应用启动时、各 endpoint 执行 startup 之前调用。"""
        pass

    def after_endpoint_startup(self):
        """应用启动时、各 endpoint 执行 startup 之后调用。"""
        pass

    def before_endpoint_shutdown(self):
        """应用关闭时、各 endpoint 执行 shutdown 之前调用。"""
        pass

    def after_endpoint_shutdown(self):
        """应用关闭时、各 endpoint 执行 shutdown 之后调用。"""
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

    def _extras(self, meta):
        return {FastAPI: self._app, CornerstoneMeta: meta}

    def _bind(self, cls, meta):
        context = getattr(self._app.state, "hive", None)
        extras = self._extras(meta)
        instance = create_hook(cls, context, extras)
        bind_cornerstone(instance, self._app, meta)
        return instance, context, extras

    def run_configure(self):
        logger.info("running cornerstone_hooks configure...")
        for cls, meta in self._pairs():
            instance, context, extras = self._bind(cls, meta)
            invoke_sync(instance, "configure", context, extras=extras)

    async def _run(self, method_name: str):
        context = getattr(self._app.state, "hive", None)
        for cls, meta in self._pairs():
            instance, _, extras = self._bind(cls, meta)
            await invoke(instance, method_name, context, extras=extras)

    async def run_before_startup_hook(self):
        logger.info("running cornerstone_hooks before endpoint startup...")
        await self._run("before_endpoint_startup")

    async def run_after_startup_hook(self):
        logger.info("running cornerstone_hooks after endpoint startup...")
        await self._run("after_endpoint_startup")

    async def run_before_shutdown_hook(self):
        logger.info("running cornerstone_hooks before endpoint shutdown...")
        await self._run("before_endpoint_shutdown")

    async def run_after_shutdown_hook(self):
        logger.info("running cornerstone_hooks after endpoint shutdown...")
        await self._run("after_endpoint_shutdown")
