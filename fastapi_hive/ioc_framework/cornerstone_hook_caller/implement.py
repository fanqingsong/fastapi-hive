

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer
from fastapi_hive.ioc_framework.cornerstone_model import Cornerstone, CornerstoneAsync, CornerstoneMeta
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
        logger.info("conerstone hook caller is starting.")

        self._app = app
        self._cornerstone_container = cornerstone_container
        self._ioc_config = ioc_config

        # print("-------------_cornerstone_container in  CornerstoneHookCaller------------------")
        # print(dir(self._cornerstone_container))

    def run_pre_setup_hook(self):
        # print("-----------_cornerstone_container in  CornerstoneHookCaller run_pre_setup_hook --------------------")
        # print(dir(self._cornerstone_container))

        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneImpl'):
                continue

            cornerstone: Cornerstone = imported_module.CornerstoneImpl(self._app)

            cornerstone.pre_setup()

    def run_post_setup_hook(self):
        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneImpl'):
                continue

            cornerstone: Cornerstone = imported_module.CornerstoneImpl(self._app)

            cornerstone.post_setup()

    def run_pre_teardown_hook(self):
        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneImpl'):
                continue

            cornerstone: Cornerstone = imported_module.CornerstoneImpl(self._app)

            cornerstone.pre_teardown()

    def run_post_teardown_hook(self):
        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneImpl'):
                continue

            cornerstone: Cornerstone = imported_module.CornerstoneImpl(self._app)

            cornerstone.post_teardown()


class CornerstoneHookAsyncCaller:
    @inject
    def __init__(
            self,
            app: FastAPI,
            cornerstone_container: CornerstoneContainer = Provide[DIContainer.cornerstone_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("conerstone hook async caller is starting.")

        self._app = app
        self._cornerstone_container = cornerstone_container
        self._ioc_config = ioc_config

        # print("-------------_cornerstone_container in  CornerstoneHookCaller------------------")
        # print(dir(self._cornerstone_container))

    async def run_pre_setup_hook(self):
        # print("-----------_cornerstone_container in  CornerstoneHookCaller run_pre_setup_hook --------------------")
        # print(dir(self._cornerstone_container))

        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneAsyncImpl'):
                continue

            cornerstone: CornerstoneAsync = imported_module.CornerstoneAsyncImpl(self._app)

            await cornerstone.pre_setup()

    async def run_post_setup_hook(self):
        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneAsyncImpl'):
                continue

            cornerstone: CornerstoneAsync = imported_module.CornerstoneAsyncImpl(self._app)

            await cornerstone.post_setup()

    async def run_pre_teardown_hook(self):
        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneAsyncImpl'):
                continue

            cornerstone: CornerstoneAsync = imported_module.CornerstoneAsyncImpl(self._app)

            await cornerstone.pre_teardown()

    async def run_post_teardown_hook(self):
        modules = self._cornerstone_container.modules
        for one_module, one_entity in modules.items():
            one_entity: CornerstoneMeta = one_entity
            imported_module = one_entity.imported_module

            if not hasattr(imported_module, 'CornerstoneAsyncImpl'):
                continue

            cornerstone: CornerstoneAsync = imported_module.CornerstoneAsyncImpl(self._app)

            await cornerstone.post_teardown()

