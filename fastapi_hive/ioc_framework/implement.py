
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
        self._load_cornerstones()

        self._load_endpoints()

        self._add_event_handler()

    def _load_cornerstones(self):
        logger.info("loading all cornerstones...")

        self._cornerstone_container.register_cornerstone_package_paths(
            self._ioc_config.CORNERSTONE_PACKAGE_PATHS
        )
        self._cornerstone_container.load_cornerstones()

    def _load_endpoints(self):
        logger.info("loading all endpoints...")

        self._endpoint_container.register_endpoint_package_paths(
            self._ioc_config.ENDPOINT_PACKAGE_PATHS
        )
        self._endpoint_container.load_endpoints()

    def _add_event_handler(self):
        logger.info("adding event handlers...")

        self._register_startup_event_handler()
        self._register_shutdown_event_handler()

    def _register_startup_event_handler(self):
        logger.info("Register startup event handler.")

        app = self._app

        app.add_event_handler("startup", self._get_sync_startup_handler())
        app.add_event_handler("startup", self._get_async_startup_handler())

    def _register_shutdown_event_handler(self):
        logger.info("Register shutdown event handler.")

        app = self._app

        app.add_event_handler("shutdown", self._get_sync_shutdown_handler())
        app.add_event_handler("shutdown", self._get_async_shutdown_handler())

    def _get_sync_startup_handler(self) -> Callable:
        app = self._app

        def run_external_pre_endpoint_setup():
            logger.info("running external sync pre endpoint setup")

            external_pre_endpoint_setup = self._ioc_config.PRE_ENDPOINT_SETUP
            if callable(external_pre_endpoint_setup):
                external_pre_endpoint_setup()

        def run_external_post_endpoint_setup():
            logger.info("running external sync post endpoint setup")

            external_post_endpoint_setup = self._ioc_config.POST_ENDPOINT_SETUP
            if callable(external_post_endpoint_setup):
                external_post_endpoint_setup()

        def startup() -> None:
            logger.info("running all sync setup handlers...")

            run_external_pre_endpoint_setup()

            self._cornerstone_hook_caller.run_pre_setup_hook()

            self._sync_setup()

            run_external_post_endpoint_setup()

            self._cornerstone_hook_caller.run_post_setup_hook()

        return startup

    def _get_sync_shutdown_handler(self) -> Callable:
        app = self._app

        def run_external_pre_endpoint_teardown():
            logger.info("running external sync pre endpoint teardown")

            external_pre_endpoint_teardown = self._ioc_config.PRE_ENDPOINT_TEARDOWN
            if callable(external_pre_endpoint_teardown):
                external_pre_endpoint_teardown()

        def run_external_post_endpoint_teardown():
            logger.info("running external sync post endpoint teardown")

            external_post_endpoint_teardown = self._ioc_config.POST_ENDPOINT_TEARDOWN
            if callable(external_post_endpoint_teardown):
                external_post_endpoint_teardown()

        def shutdown() -> None:
            logger.info("running all sync teardown handlers...")

            run_external_pre_endpoint_teardown()

            self._cornerstone_hook_caller.run_pre_teardown_hook()

            self._sync_teardown()

            run_external_post_endpoint_teardown()

            self._cornerstone_hook_caller.run_post_teardown_hook()

        return shutdown

    def _get_async_startup_handler(self) -> Callable:
        app = self._app

        async def run_external_async_pre_endpoint_setup():
            logger.info("running external async pre endpoint setup.")

            external_async_pre_endpoint_setup = self._ioc_config.ASYNC_PRE_ENDPOINT_SETUP
            if callable(external_async_pre_endpoint_setup):
                await external_async_pre_endpoint_setup()

        async def run_external_async_post_endpoint_setup():
            logger.info("running external async post endpoint setup")

            external_async_post_endpoint_setup = self._ioc_config.ASYNC_POST_ENDPOINT_SETUP
            if callable(external_async_post_endpoint_setup):
                await external_async_post_endpoint_setup()

        async def startup() -> None:
            logger.info("running all async setup handlers...")

            await run_external_async_pre_endpoint_setup()

            await self._cornerstone_hook_async_caller.run_pre_setup_hook()

            await self._async_setup()

            await run_external_async_post_endpoint_setup()

            await self._cornerstone_hook_async_caller.run_post_setup_hook()

        return startup

    def _get_async_shutdown_handler(self) -> Callable:
        app = self._app

        async def run_external_async_pre_endpoint_teardown():
            logger.info("running external async pre endpoint teardown")

            external_async_pre_endpoint_teardown = self._ioc_config.ASYNC_PRE_ENDPOINT_TEARDOWN
            if callable(external_async_pre_endpoint_teardown):
                await external_async_pre_endpoint_teardown()

        async def run_external_async_post_endpoint_teardown():
            logger.info("running external async post endpoint teardown")

            external_async_post_endpoint_teardown = self._ioc_config.ASYNC_POST_ENDPOINT_TEARDOWN
            if callable(external_async_post_endpoint_teardown):
                await external_async_post_endpoint_teardown()

        async def shutdown() -> None:
            logger.info("running all async teardown handlers...")

            await run_external_async_pre_endpoint_teardown()

            await self._cornerstone_hook_async_caller.run_pre_teardown_hook()

            await self._async_teardown()

            await run_external_async_post_endpoint_teardown()

            await self._cornerstone_hook_async_caller.run_post_teardown_hook()

        return shutdown

    def _sync_setup(self) -> None:
        logger.info("running sync endpoint setup...")

        self._endpoint_hook_caller.run_setup_hook()
        self._endpoint_router_mounter.mount(self._ioc_config.API_PREFIX)

    def _sync_teardown(self) -> None:
        logger.info("running sync endpoint teardown...")

        self._endpoint_hook_caller.run_teardown_hook()
        self._endpoint_router_mounter.unmount(self._ioc_config.API_PREFIX)

    async def _async_setup(self) -> None:
        logger.info("running async endpoint setup...")

        await self._endpoint_hook_async_caller.run_setup_hook()

    async def _async_teardown(self) -> None:
        logger.info("running async endpoint teardown...")

        await self._endpoint_hook_async_caller.run_teardown_hook()


