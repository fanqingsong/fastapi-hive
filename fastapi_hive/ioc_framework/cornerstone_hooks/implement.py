from typing import Callable, Optional
from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer, CornerstoneMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi import FastAPI
from abc import ABC, abstractmethod
from starlette.requests import Request


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

    def pre_endpoint_setup(self):
        pass

    def post_endpoint_setup(self):
        pass

    def pre_endpoint_teardown(self):
        pass

    def post_endpoint_teardown(self):
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
        async def pre_endpoint_setup(self):
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

    async def pre_endpoint_setup(self):
        pass

    async def post_endpoint_setup(self):
        pass

    async def pre_endpoint_teardown(self):
        pass

    async def post_endpoint_teardown(self):
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

    def _iterate_cornerstones(self, callback: Callable):
        def callback_iter(cornerstone_meta: CornerstoneMeta):
            imported_module = cornerstone_meta.imported_module

            if not hasattr(imported_module, 'CornerstoneHooksImpl'):
                return

            app: FastAPI = self._app

            cornerstone_hooks: CornerstoneHooks = imported_module.CornerstoneHooksImpl()
            cornerstone_hooks.app = app
            cornerstone_hooks.cornerstone = cornerstone_meta

            pkg_path = f'{cornerstone_meta.container_name}.{cornerstone_meta.name}'
            cornerstone_hooks.app_state = app.state.cornerstones[pkg_path]

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

    def run_pre_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks sync pre endpoint call...")

        def callback(cornerstone_hooks: CornerstoneHooks):
            cornerstone_meta: CornerstoneMeta = cornerstone_hooks.cornerstone

            pkg_path = f'{cornerstone_meta.container_name}.{cornerstone_meta.name}'
            cornerstone_hooks.request_state = request.state.cornerstones[pkg_path]

            cornerstone_hooks.request = request
            cornerstone_hooks.pre_endpoint_call()

        self._iterate_cornerstones(callback)

    def run_post_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks sync post endpoint call...")

        def callback(cornerstone_hooks: CornerstoneHooks):
            cornerstone_meta: CornerstoneMeta = cornerstone_hooks.cornerstone

            pkg_path = f'{cornerstone_meta.container_name}.{cornerstone_meta.name}'
            cornerstone_hooks.request_state = request.state.cornerstones[pkg_path]

            cornerstone_hooks.request = request
            cornerstone_hooks.post_endpoint_call()

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

            app: FastAPI = self._app

            cornerstone_hooks: CornerstoneAsyncHooks = imported_module.CornerstoneAsyncHooksImpl()
            cornerstone_hooks.app = app
            cornerstone_hooks.cornerstone = cornerstone_meta

            pkg_path = f'{cornerstone_meta.container_name}.{cornerstone_meta.name}'
            cornerstone_hooks.app_state = app.state.cornerstones[pkg_path]

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

    async def run_pre_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks async pre endpoint call...")

        async def callback(cornerstone_hooks: CornerstoneAsyncHooks):
            cornerstone_meta: CornerstoneMeta = cornerstone_hooks.cornerstone

            pkg_path = f'{cornerstone_meta.container_name}.{cornerstone_meta.name}'
            cornerstone_hooks.req_state = request.state.cornerstones[pkg_path]

            cornerstone_hooks.request = request
            await cornerstone_hooks.pre_endpoint_call()

        await self._iterate_cornerstones(callback)

    async def run_post_call_hook(self, request: Request):
        logger.info("running cornerstone_hooks async post endpoint call...")

        async def callback(cornerstone_hooks: CornerstoneAsyncHooks):
            cornerstone_meta: CornerstoneMeta = cornerstone_hooks.cornerstone

            pkg_path = f'{cornerstone_meta.container_name}.{cornerstone_meta.name}'
            cornerstone_hooks.req_state = request.state.cornerstones[pkg_path]

            cornerstone_hooks.request = request
            await cornerstone_hooks.post_endpoint_call()

        await self._iterate_cornerstones(callback)
