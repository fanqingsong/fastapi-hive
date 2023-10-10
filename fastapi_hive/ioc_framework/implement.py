
from fastapi import FastAPI
from typing import Callable
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer
from fastapi_hive.ioc_framework.endpoint_router_mounter import EndpointRouterMounter
from fastapi_hive.ioc_framework.cornerstone_hook_caller import CornerstoneHookCaller, CornerstoneHookAsyncCaller
from fastapi_hive.ioc_framework.endpoint_hook_caller import EndpointHookCaller, EndpointHookAsyncCaller
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer


class IoCFramework:
    @inject
    def __init__(
        self,
        app: FastAPI,
        ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
        endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container],
        cornerstone_container: CornerstoneContainer = Provide[DIContainer.cornerstone_container],
    ):
        self._app = app
        self._ioc_config: IoCConfig = ioc_config

        self._endpoint_container = endpoint_container
        self._cornerstone_container = cornerstone_container

        self._endpoint_router_mounter = EndpointRouterMounter(app)

        self._cornerstone_hook_caller = CornerstoneHookCaller(app)
        self._cornerstone_hook_async_caller = CornerstoneHookAsyncCaller(app)

        self._endpoint_hook_caller = EndpointHookCaller(app)
        self._endpoint_hook_async_caller = EndpointHookAsyncCaller(app)

    @property
    def config(self):
        return self._ioc_config

    def init_modules(self) -> None:
        self._cornerstone_container.register_module_package_paths(
            self._ioc_config.CORNERSTONE_PACKAGE_PATHS
        )
        self._cornerstone_container.resolve_modules()

        self._endpoint_container.register_module_package_paths(
            self._ioc_config.MODULE_PACKAGE_PATHS
        )
        self._endpoint_container.resolve_modules()

        self._add_sync_event_handler()
        self._add_async_event_handler()

    def _add_sync_event_handler(self):
        logger.info("Register sync event handler.")

        app = self._app
        app.add_event_handler("startup", self._start_ioc_sync_handler())
        app.add_event_handler("shutdown", self._stop_ioc_sync_handler())

    def _add_async_event_handler(self):
        logger.info("Register async event handler.")

        app = self._app
        app.add_event_handler("startup", self._start_ioc_async_handler())
        app.add_event_handler("shutdown", self._stop_ioc_async_handler())

    def _sync_setup(self) -> None:
        self._endpoint_hook_caller.run_setup_hook()

        self._endpoint_router_mounter.mount(self._ioc_config.API_PREFIX)

    def _sync_teardown(self) -> None:
        self._endpoint_hook_caller.run_teardown_hook()

        self._endpoint_router_mounter.unmount(self._ioc_config.API_PREFIX)

    async def _async_setup(self) -> None:
        await self._endpoint_hook_async_caller.run_setup_hook()

    async def _async_teardown(self) -> None:
        await self._endpoint_hook_async_caller.run_teardown_hook()

    def _start_ioc_sync_handler(self) -> Callable:
        app = self._app

        def run_ioc_pre_setup():
            hive_pre_setup = self._ioc_config.PRE_SETUP
            if callable(hive_pre_setup):
                logger.info("call hive pre setup")
                hive_pre_setup()

        def run_ioc_post_setup():
            hive_post_setup = self._ioc_config.POST_SETUP
            if callable(hive_post_setup):
                logger.info("call hive post setup")
                hive_post_setup()

        def startup() -> None:
            logger.info("Running container sync start handler.")

            self._cornerstone_hook_caller.run_pre_setup_hook()

            run_ioc_pre_setup()

            self._sync_setup()

            self._cornerstone_hook_caller.run_post_setup_hook()

            run_ioc_post_setup()

        return startup

    def _stop_ioc_sync_handler(self) -> Callable:
        app = self._app

        def run_ioc_pre_teardown():
            hive_pre_teardown = self._ioc_config.PRE_TEARDOWN
            if callable(hive_pre_teardown):
                logger.info("call hive pre teardown")
                hive_pre_teardown()

        def run_ioc_post_teardown():
            hive_post_teardown = self._ioc_config.POST_TEARDOWN
            if callable(hive_post_teardown):
                logger.info("call hive post teardown")
                hive_post_teardown()

        def shutdown() -> None:
            logger.info("Running container sync shutdown handler.")

            self._cornerstone_hook_caller.run_pre_teardown_hook()

            run_ioc_pre_teardown()

            self._sync_teardown()

            self._cornerstone_hook_caller.run_post_teardown_hook()

            run_ioc_post_teardown()

        return shutdown

    def _start_ioc_async_handler(self) -> Callable:
        app = self._app

        async def run_ioc_pre_setup():
            hive_pre_setup = self._ioc_config.ASYNC_PRE_SETUP
            if callable(hive_pre_setup):
                logger.info("call hive pre setup")
                await hive_pre_setup()

        async def run_ioc_post_setup():
            hive_post_setup = self._ioc_config.ASYNC_POST_SETUP
            if callable(hive_post_setup):
                logger.info("call hive post setup")
                await hive_post_setup()

        async def startup() -> None:
            logger.info("Running container async start handler.")

            await self._cornerstone_hook_async_caller.run_pre_setup_hook()

            await run_ioc_pre_setup()

            await self._async_setup()

            await self._cornerstone_hook_async_caller.run_post_setup_hook()

            await run_ioc_post_setup()

        return startup

    def _stop_ioc_async_handler(self) -> Callable:
        app = self._app

        async def run_ioc_pre_teardown():
            hive_pre_teardown = self._ioc_config.ASYNC_PRE_TEARDOWN
            if callable(hive_pre_teardown):
                logger.info("call hive pre teardown")
                await hive_pre_teardown()

        async def run_ioc_post_teardown():
            hive_post_teardown = self._ioc_config.ASYNC_POST_TEARDOWN
            if callable(hive_post_teardown):
                logger.info("call hive post teardown")
                await hive_post_teardown()

        async def shutdown() -> None:
            logger.info("Running container async shutdown handler.")

            await self._cornerstone_hook_async_caller.run_pre_teardown_hook()

            await run_ioc_pre_teardown()

            await self._async_teardown()

            await self._cornerstone_hook_async_caller.run_post_teardown_hook()

            await run_ioc_post_teardown()

        return shutdown
