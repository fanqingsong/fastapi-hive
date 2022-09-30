
from fastapi import FastAPI
from typing import Callable, Dict, List
from loguru import logger
from fastapi_modules.ioc_framework.module_container import module_container
from fastapi_modules.ioc_framework.router_mounter import RouterMounter
from fastapi_modules.ioc_framework.module_mounter import ModuleMounter
from fastapi_modules.ioc_framework.config import Config


class IoCFramework:
    def __init__(self, app: FastAPI):
        self._app = app
        self._config: Config = Config()
        self._router_mounter = RouterMounter(app)
        self._module_mounter = ModuleMounter(app)

    @property
    def config(self):
        return self._config

    def init_modules(self) -> None:
        module_container.register_module_package_paths(
            self._config.MODULE_PACKAGE_PATHS)
        module_container.resolve_modules()

        app = self._app
        app.add_event_handler("startup", self._start_container_handler())
        app.add_event_handler("shutdown", self._stop_container_handler())

    def add_modules_by_packages(self, module_package_paths):
        module_container.register_module_package_paths(module_package_paths)
        module_container.resolve_modules()

        self._teardown()
        self._setup()

    def delete_modules_by_packages(self, module_package_paths):
        module_container.unregister_module_package_paths(module_package_paths)
        module_container.resolve_modules()

        self._teardown()
        self._setup()

    def _setup(self) -> None:
        self._module_mounter.mount()
        self._router_mounter.mount(self._config.API_PREFIX)

    def _teardown(self) -> None:
        self._module_mounter.unmount()
        self._router_mounter.unmount(self._config.API_PREFIX)

    def _start_container_handler(self) -> Callable:
        def startup() -> None:
            logger.info("Running container start handler.")

            self._setup()
        return startup

    def _stop_container_handler(self) -> Callable:
        def shutdown() -> None:
            logger.info("Running container shutdown handler.")

            self._teardown()
        return shutdown
