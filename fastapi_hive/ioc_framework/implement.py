import os
import time
from collections import defaultdict
from typing import Any, Callable, Dict, Optional, Union

from fastapi import FastAPI
from loguru import logger
from starlette.requests import Request
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer
from fastapi_hive.ioc_framework.endpoint_router_mounter import EndpointRouterMounter
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHookCaller, CornerstoneHookAsyncCaller
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHookCaller, EndpointHookAsyncCaller
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.registry import HiveRegistry
from fastapi_hive.ioc_framework.hive_settings import (
    apply_hive_settings,
    dump_config,
)


class IoCFramework:
    @inject
    def __init__(
        self,
        app: FastAPI,
        settings: Optional[Union[IoCConfig, Dict[str, Any]]] = None,
        config_path: Optional[str] = None,
        ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
        endpoint_container: EndpointContainer = Provide[
            DIContainer.endpoint_container
        ],
        cornerstone_container: CornerstoneContainer = Provide[
            DIContainer.cornerstone_container
        ],
    ):
        self._app = app
        self._ioc_config: IoCConfig = ioc_config
        overrides = (
            dump_config(settings) if isinstance(settings, IoCConfig) else settings
        )
        apply_hive_settings(
            self._ioc_config,
            config_path=config_path,
            overrides=overrides,
        )

        self._endpoint_container = endpoint_container
        self._cornerstone_container = cornerstone_container

        self._endpoint_router_mounter = EndpointRouterMounter(app)

        self._cornerstone_hook_caller = CornerstoneHookCaller(app)
        self._cornerstone_hook_async_caller = CornerstoneHookAsyncCaller(app)

        self._endpoint_hook_caller = EndpointHookCaller(app)
        self._endpoint_hook_async_caller = EndpointHookAsyncCaller(app)

    @classmethod
    def bootstrap(
        cls,
        app: FastAPI,
        settings: Optional[Union[IoCConfig, Dict[str, Any]]] = None,
        config_path: Optional[str] = None,
    ) -> "IoCFramework":
        hive = cls(app, settings=settings, config_path=config_path)
        hive.init_modules()
        return hive

    @property
    def config(self):
        return self._ioc_config

    def init_modules(self) -> None:
        self._load_cornerstones()
        self._load_endpoints()

        # set cornerstone state as app state to expose for endpoint access, such as db instance
        self._app.state.cornerstones = self._get_initial_cornerstone_state()

        # set endpoint state as app state to expose for endpoint access, such as ML model instance
        self._app.state.endpoints = self._get_initial_endpoint_state()
        self._app.state.hive = HiveRegistry()

        # Starlette requires middleware to be registered before the application
        # starts. Cornerstone pre-startup commonly installs shared middleware, so
        # synchronous preparation must happen while the app is being assembled.
        self._cornerstone_hook_caller.run_pre_startup_hook()

        self._add_event_handler()

        self._add_http_middleware()

    def _get_initial_cornerstone_state(self):
        cornerstones = self._cornerstone_container.cornerstones

        state = defaultdict(dict)
        for pkg_path, cornerstone in cornerstones.items():
            state[pkg_path] = {}
            state[pkg_path]['__cornerstone__'] = cornerstone

        return state

    def _get_initial_endpoint_state(self):
        endpoints = self._endpoint_container.endpoints

        state = defaultdict(dict)
        for pkg_path, endpoint in endpoints.items():
            state[pkg_path] = {}
            state[pkg_path]['__endpoint__'] = endpoint

        return state

    def _add_http_middleware(self):
        app = self._app

        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            start_time = time.time()

            request.state.cornerstones = self._get_initial_cornerstone_state()
            request.state.hive = HiveRegistry()

            self._cornerstone_hook_caller.run_pre_call_hook(request)

            await self._cornerstone_hook_async_caller.run_pre_call_hook(request)

            response = await call_next(request)

            self._cornerstone_hook_caller.run_post_call_hook(request)

            await self._cornerstone_hook_async_caller.run_post_call_hook(request)

            process_time = time.time() - start_time

            response.headers["X-Process-Time"] = str(process_time)
            logger.info(f'process_time = {process_time}')

            return response

    def _load_cornerstones(self):
        logger.info("loading all cornerstones...")

        package_path = self._ioc_config.CORNERSTONE_PACKAGE_PATH
        if not package_path or not os.path.isdir(package_path):
            logger.info("no cornerstone package directory, skip loading.")
            return

        self._cornerstone_container.register_cornerstone_package_path(package_path)
        self._cornerstone_container.load_cornerstones()

    def _load_endpoints(self):
        logger.info("loading all endpoints...")

        package_paths = [
            path for path in self._ioc_config.ENDPOINT_PACKAGE_PATHS
            if path and os.path.isdir(path)
        ]
        if not package_paths:
            logger.info("no endpoint package directory, skip loading.")
            return

        self._endpoint_container.register_endpoint_package_paths(package_paths)
        self._endpoint_container.load_endpoints()

    def _add_event_handler(self):
        logger.info("adding event handlers...")

        self._register_startup_event_handler()
        self._register_shutdown_event_handler()

    def _register_startup_event_handler(self):
        logger.info("Register startup event handler.")

        app = self._app

        app.router.add_event_handler("startup", self._get_sync_startup_handler())
        app.router.add_event_handler("startup", self._get_async_startup_handler())

    def _register_shutdown_event_handler(self):
        logger.info("Register shutdown event handler.")

        app = self._app

        app.router.add_event_handler("shutdown", self._get_sync_shutdown_handler())
        app.router.add_event_handler("shutdown", self._get_async_shutdown_handler())

    def _get_sync_startup_handler(self) -> Callable:
        app = self._app

        def run_external_pre_endpoint_startup():
            logger.info("running external sync pre endpoint startup")

            external_pre_endpoint_startup = self._ioc_config.PRE_ENDPOINT_STARTUP
            if callable(external_pre_endpoint_startup):
                external_pre_endpoint_startup()

        def run_external_post_endpoint_startup():
            logger.info("running external sync post endpoint startup")

            external_post_endpoint_startup = self._ioc_config.POST_ENDPOINT_STARTUP
            if callable(external_post_endpoint_startup):
                external_post_endpoint_startup()

        def startup() -> None:
            logger.info("running all sync startup handlers...")

            run_external_pre_endpoint_startup()

            self._sync_startup()

            run_external_post_endpoint_startup()

            self._cornerstone_hook_caller.run_post_startup_hook()

        return startup

    def _get_sync_shutdown_handler(self) -> Callable:
        app = self._app

        def run_external_pre_endpoint_shutdown():
            logger.info("running external sync pre endpoint shutdown")

            external_pre_endpoint_shutdown = self._ioc_config.PRE_ENDPOINT_SHUTDOWN
            if callable(external_pre_endpoint_shutdown):
                external_pre_endpoint_shutdown()

        def run_external_post_endpoint_shutdown():
            logger.info("running external sync post endpoint shutdown")

            external_post_endpoint_shutdown = self._ioc_config.POST_ENDPOINT_SHUTDOWN
            if callable(external_post_endpoint_shutdown):
                external_post_endpoint_shutdown()

        def shutdown() -> None:
            logger.info("running all sync shutdown handlers...")

            run_external_pre_endpoint_shutdown()

            self._cornerstone_hook_caller.run_pre_shutdown_hook()

            self._sync_shutdown()

            run_external_post_endpoint_shutdown()

            self._cornerstone_hook_caller.run_post_shutdown_hook()

        return shutdown

    def _get_async_startup_handler(self) -> Callable:
        app = self._app

        async def run_external_async_pre_endpoint_startup():
            logger.info("running external async pre endpoint startup.")

            external_async_pre_endpoint_startup = self._ioc_config.ASYNC_PRE_ENDPOINT_STARTUP
            if callable(external_async_pre_endpoint_startup):
                await external_async_pre_endpoint_startup()

        async def run_external_async_post_endpoint_startup():
            logger.info("running external async post endpoint startup")

            external_async_post_endpoint_startup = self._ioc_config.ASYNC_POST_ENDPOINT_STARTUP
            if callable(external_async_post_endpoint_startup):
                await external_async_post_endpoint_startup()

        async def startup() -> None:
            logger.info("running all async startup handlers...")

            await run_external_async_pre_endpoint_startup()

            await self._cornerstone_hook_async_caller.run_pre_startup_hook()

            await self._async_startup()

            await run_external_async_post_endpoint_startup()

            await self._cornerstone_hook_async_caller.run_post_startup_hook()

        return startup

    def _get_async_shutdown_handler(self) -> Callable:
        app = self._app

        async def run_external_async_pre_endpoint_shutdown():
            logger.info("running external async pre endpoint shutdown")

            external_async_pre_endpoint_shutdown = self._ioc_config.ASYNC_PRE_ENDPOINT_SHUTDOWN
            if callable(external_async_pre_endpoint_shutdown):
                await external_async_pre_endpoint_shutdown()

        async def run_external_async_post_endpoint_shutdown():
            logger.info("running external async post endpoint shutdown")

            external_async_post_endpoint_shutdown = self._ioc_config.ASYNC_POST_ENDPOINT_SHUTDOWN
            if callable(external_async_post_endpoint_shutdown):
                await external_async_post_endpoint_shutdown()

        async def shutdown() -> None:
            logger.info("running all async shutdown handlers...")

            await run_external_async_pre_endpoint_shutdown()

            await self._cornerstone_hook_async_caller.run_pre_shutdown_hook()

            await self._async_shutdown()

            await run_external_async_post_endpoint_shutdown()

            await self._cornerstone_hook_async_caller.run_post_shutdown_hook()

        return shutdown

    def _sync_startup(self) -> None:
        logger.info("running sync endpoint startup...")

        self._endpoint_hook_caller.run_startup_hook()

        if self._ioc_config.ROUTER_MOUNT_AUTOMATED:
            self._endpoint_router_mounter.mount()

    def _sync_shutdown(self) -> None:
        logger.info("running sync endpoint shutdown...")

        self._endpoint_hook_caller.run_shutdown_hook()

    async def _async_startup(self) -> None:
        logger.info("running async endpoint startup...")

        await self._endpoint_hook_async_caller.run_startup_hook()

    async def _async_shutdown(self) -> None:
        logger.info("running async endpoint shutdown...")

        await self._endpoint_hook_async_caller.run_shutdown_hook()


