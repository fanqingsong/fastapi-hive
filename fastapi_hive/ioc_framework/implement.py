
from fastapi import FastAPI
from typing import Callable
from loguru import logger
from fastapi_hive.ioc_framework.module_container import ModuleContainer
from fastapi_hive.ioc_framework.router_mounter import RouterMounter
from fastapi_hive.ioc_framework.module_mounter import ModuleMounter
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer


class IoCFramework:
    @inject
    def __init__(
        self,
        app: FastAPI,
        ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
        module_container: ModuleContainer = Provide[DIContainer.module_container],
    ):
        self._app = app
        self._ioc_config: IoCConfig = ioc_config
        self._module_container = module_container
        self._router_mounter = RouterMounter(app)
        self._module_mounter = ModuleMounter(app)

    @property
    def config(self):
        return self._ioc_config

    def init_modules(self) -> None:
        self._module_container.register_module_package_paths(
            self._ioc_config.MODULE_PACKAGE_PATHS
        )
        self._module_container.resolve_modules()

        app = self._app
        app.add_event_handler("startup", self._start_ioc_handler())
        app.add_event_handler("shutdown", self._stop_ioc_handler())

    def add_modules_by_packages(self, module_package_paths):
        self._module_container.register_module_package_paths(module_package_paths)
        self._module_container.resolve_modules()

        self._teardown()
        self._setup()

    def delete_modules_by_packages(self, module_package_paths):
        self._module_container.unregister_module_package_paths(module_package_paths)
        self._module_container.resolve_modules()

        self._teardown()
        self._setup()

    def _setup(self) -> None:
        self._module_mounter.mount()
        self._router_mounter.mount(self._ioc_config.API_PREFIX)

    def _teardown(self) -> None:
        self._module_mounter.unmount()
        self._router_mounter.unmount(self._ioc_config.API_PREFIX)

    def _start_ioc_handler(self) -> Callable:
        app = self._app

        def startup() -> None:
            logger.info("Running container start handler.")

            hive_pre_stetup = self._ioc_config.PRE_SETUP
            if callable(hive_pre_stetup):
                logger.info("call hive pre setup")
                hive_pre_stetup()

            self._setup()

            hive_post_stetup = self._ioc_config.POST_SETUP
            if callable(hive_post_stetup):
                logger.info("call hive post setup")
                hive_post_stetup()

        return startup

    def _stop_ioc_handler(self) -> Callable:
        app = self._app

        def shutdown() -> None:
            logger.info("Running container shutdown handler.")

            hive_pre_teardown = self._ioc_config.PRE_TEARDOWN
            if callable(hive_pre_teardown):
                logger.info("call hive pre teardown")
                hive_pre_teardown()

            self._teardown()

            hive_post_teardown = self._ioc_config.POST_TEARDOWN
            if callable(hive_post_teardown):
                logger.info("call hive post teardown")
                hive_post_teardown()

        return shutdown
