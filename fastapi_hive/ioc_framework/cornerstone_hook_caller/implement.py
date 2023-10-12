from typing import Callable

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer
from fastapi_hive.ioc_framework.cornerstone_model import CornerstoneHooks, CornerstoneAsyncHooks, CornerstoneMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


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
        cornerstones = self._cornerstone_container.cornerstones
        for _, one_cornerstone in cornerstones.items():
            one_cornerstone: CornerstoneMeta = one_cornerstone
            imported_module = one_cornerstone.imported_module

            if not hasattr(imported_module, 'CornerstoneHooksImpl'):
                continue

            cornerstone: CornerstoneHooks = imported_module.CornerstoneHooksImpl(self._app)

            callback(cornerstone)

    def run_pre_setup_hook(self):
        logger.info("running cornerstone sync pre endpoint setup...")

        def callback(cornerstone: CornerstoneHooks):
            cornerstone.pre_endpoint_setup()

        self._iterate_cornerstones(callback)

    def run_post_setup_hook(self):
        logger.info("running cornerstone sync post endpoint setup...")

        def callback(cornerstone: CornerstoneHooks):
            cornerstone.post_endpoint_setup()

        self._iterate_cornerstones(callback)

    def run_pre_teardown_hook(self):
        logger.info("running cornerstone sync pre endpoint teardown...")

        def callback(cornerstone: CornerstoneHooks):
            cornerstone.pre_endpoint_teardown()

        self._iterate_cornerstones(callback)

    def run_post_teardown_hook(self):
        logger.info("running cornerstone sync post endpoint teardown...")

        def callback(cornerstone: CornerstoneHooks):
            cornerstone.post_endpoint_teardown()

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
        cornerstones = self._cornerstone_container.cornerstones
        for _, one_cornerstone in cornerstones.items():
            one_cornerstone: CornerstoneMeta = one_cornerstone
            imported_module = one_cornerstone.imported_module

            if not hasattr(imported_module, 'CornerstoneAsyncHooksImpl'):
                continue

            cornerstone: CornerstoneAsyncHooks = imported_module.CornerstoneAsyncHooksImpl(self._app)

            await callback(cornerstone)

    async def run_pre_setup_hook(self):
        logger.info("running cornerstone async pre endpoint setup...")

        async def callback(cornerstone: CornerstoneAsyncHooks):
            await cornerstone.pre_endpoint_setup()

        await self._iterate_cornerstones(callback)

    async def run_post_setup_hook(self):
        logger.info("running cornerstone async post endpoint setup...")

        async def callback(cornerstone: CornerstoneAsyncHooks):
            await cornerstone.post_endpoint_setup()

        await self._iterate_cornerstones(callback)

    async def run_pre_teardown_hook(self):
        logger.info("running cornerstone async pre endpoint teardown...")

        async def callback(cornerstone: CornerstoneAsyncHooks):
            await cornerstone.pre_endpoint_teardown()

        await self._iterate_cornerstones(callback)

    async def run_post_teardown_hook(self):
        logger.info("running cornerstone async post endpoint teardown...")

        async def callback(cornerstone: CornerstoneAsyncHooks):
            await cornerstone.post_endpoint_teardown()

        await self._iterate_cornerstones(callback)


