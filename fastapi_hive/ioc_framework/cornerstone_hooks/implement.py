from typing import Callable

from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer, CornerstoneMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi import FastAPI
from abc import ABC,abstractmethod


class CornerstoneHooks(ABC):
    '''
    Base class for cornerstone hooks.

    Usage
    ===

    In your cornerstone cornerstones `__init__.py` create a subclass of `CornerstoneHooks`

    ```python
    from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneHooks


    class CornerstoneImpl(CornerstoneHooks):
        def pre_endpoint_setup(self):
            pass
    ```
    '''

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    @abstractmethod
    def pre_endpoint_setup(self):
        pass

    @abstractmethod
    def post_endpoint_setup(self):
        pass

    @abstractmethod
    def pre_endpoint_teardown(self):
        pass

    @abstractmethod
    def post_endpoint_teardown(self):
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
        async def pre_endpoint_setup(self):
            pass
    ```
    '''

    def __init__(self, app: FastAPI) -> None:
        self._app = app

    @abstractmethod
    async def pre_endpoint_setup(self):
        pass

    @abstractmethod
    async def post_endpoint_setup(self):
        pass

    @abstractmethod
    async def pre_endpoint_teardown(self):
        pass

    @abstractmethod
    async def post_endpoint_teardown(self):
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

    def _iterate_cornerstones(self, callback: Callable):
        def callback_iter(cornerstone_meta: CornerstoneMeta):
            imported_module = cornerstone_meta.imported_module

            if not hasattr(imported_module, 'CornerstoneHooksImpl'):
                return

            cornerstone_hooks: CornerstoneHooks = imported_module.CornerstoneHooksImpl(self._app)

            callback(cornerstone_hooks)

        self._cornerstone_container.iterate_cornerstones(callback_iter)

    def run_pre_setup_hook(self):
        logger.info("running cornerstone_hooks sync pre endpoint setup...")

        def callback(cornerstone_hooks: CornerstoneHooks):
            cornerstone_hooks.pre_endpoint_setup()

        self._iterate_cornerstones(callback)

    def run_post_setup_hook(self):
        logger.info("running cornerstone_hooks sync post endpoint setup...")

        def callback(cornerstone_hooks: CornerstoneHooks):
            cornerstone_hooks.post_endpoint_setup()

        self._iterate_cornerstones(callback)

    def run_pre_teardown_hook(self):
        logger.info("running cornerstone_hooks sync pre endpoint teardown...")

        def callback(cornerstone_hooks: CornerstoneHooks):
            cornerstone_hooks.pre_endpoint_teardown()

        self._iterate_cornerstones(callback)

    def run_post_teardown_hook(self):
        logger.info("running cornerstone_hooks sync post endpoint teardown...")

        def callback(cornerstone_hooks: CornerstoneHooks):
            cornerstone_hooks.post_endpoint_teardown()

        self._iterate_cornerstones(callback)


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

    async def _iterate_cornerstones(self, callback: Callable):
        async def callback_iter(cornerstone_meta: CornerstoneMeta):
            imported_module = cornerstone_meta.imported_module

            if not hasattr(imported_module, 'CornerstoneAsyncHooksImpl'):
                return

            cornerstone_hooks: CornerstoneAsyncHooks = imported_module.CornerstoneAsyncHooksImpl(self._app)

            await callback(cornerstone_hooks)

        await self._cornerstone_container.async_iterate_cornerstones(callback_iter)

    async def run_pre_setup_hook(self):
        logger.info("running cornerstone_hooks async pre endpoint setup...")

        async def callback(cornerstone_hooks: CornerstoneAsyncHooks):
            await cornerstone_hooks.pre_endpoint_setup()

        await self._iterate_cornerstones(callback)

    async def run_post_setup_hook(self):
        logger.info("running cornerstone_hooks async post endpoint setup...")

        async def callback(cornerstone_hooks: CornerstoneAsyncHooks):
            await cornerstone_hooks.post_endpoint_setup()

        await self._iterate_cornerstones(callback)

    async def run_pre_teardown_hook(self):
        logger.info("running cornerstone_hooks async pre endpoint teardown...")

        async def callback(cornerstone_hooks: CornerstoneAsyncHooks):
            await cornerstone_hooks.pre_endpoint_teardown()

        await self._iterate_cornerstones(callback)

    async def run_post_teardown_hook(self):
        logger.info("running cornerstone_hooks async post endpoint teardown...")

        async def callback(cornerstone_hooks: CornerstoneAsyncHooks):
            await cornerstone_hooks.post_endpoint_teardown()

        await self._iterate_cornerstones(callback)


