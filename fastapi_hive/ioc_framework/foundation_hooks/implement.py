from typing import Optional
from loguru import logger
from fastapi_hive.ioc_framework.foundation_container import FoundationContainer, FoundationMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi import FastAPI
from abc import ABC
from fastapi_hive.ioc_framework.decorators import (
    bind_foundation,
    create_hook,
    invoke,
    invoke_sync,
    select_hooks,
)


class FoundationHooks(ABC):
    '''
    Base class for foundation hooks.

    Usage
    ===

    In your foundation `__init__.py` create a subclass of `FoundationHooks`

    ```python
    from fastapi_hive.ioc_framework.foundation_hooks import FoundationHooks


    class FoundationImpl(FoundationHooks):
        def configure(self):
            pass
    ```
    '''

    def __init__(self) -> None:
        self._app: Optional[FastAPI] = None
        self._foundation: Optional[FoundationMeta] = None

    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, value: FastAPI):
        self._app = value

    @property
    def foundation(self):
        return self._foundation

    @foundation.setter
    def foundation(self, value: FoundationMeta):
        self._foundation = value

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


class FoundationHookCaller:
    @inject
    def __init__(
            self,
            app: FastAPI,
            foundation_container: FoundationContainer = Provide[DIContainer.foundation_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("foundation hook caller is initializing.")

        self._app = app
        self._foundation_container = foundation_container
        self._ioc_config = ioc_config

    def _pairs(self):
        pairs = []
        for meta in self._foundation_container.foundations.values():
            for cls in meta.hooks:
                pairs.append((cls, meta))
        return select_hooks(pairs, self._ioc_config)

    def _extras(self, meta):
        return {FastAPI: self._app, FoundationMeta: meta}

    def _bind(self, cls, meta):
        context = getattr(self._app.state, "hive", None)
        extras = self._extras(meta)
        instance = create_hook(cls, context, extras)
        bind_foundation(instance, self._app, meta)
        return instance, context, extras

    def run_configure(self):
        logger.info("running foundation_hooks configure...")
        for cls, meta in self._pairs():
            instance, context, extras = self._bind(cls, meta)
            invoke_sync(instance, "configure", context, extras=extras)

    async def _run(self, method_name: str):
        context = getattr(self._app.state, "hive", None)
        for cls, meta in self._pairs():
            instance, _, extras = self._bind(cls, meta)
            await invoke(instance, method_name, context, extras=extras)

    async def run_before_startup_hook(self):
        logger.info("running foundation_hooks before endpoint startup...")
        await self._run("before_endpoint_startup")

    async def run_after_startup_hook(self):
        logger.info("running foundation_hooks after endpoint startup...")
        await self._run("after_endpoint_startup")

    async def run_before_shutdown_hook(self):
        logger.info("running foundation_hooks before endpoint shutdown...")
        await self._run("before_endpoint_shutdown")

    async def run_after_shutdown_hook(self):
        logger.info("running foundation_hooks after endpoint shutdown...")
        await self._run("after_endpoint_shutdown")
