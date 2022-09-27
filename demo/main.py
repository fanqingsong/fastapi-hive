

from fastapi import FastAPI
from loguru import logger
from demo.core.config import (APP_NAME, APP_VERSION, API_PREFIX,
                                         IS_DEBUG)

from fastapi_modules.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    ioc_framework = IoCFramework(fast_app)
    ioc_framework.config.API_PREFIX = API_PREFIX
    ioc_framework.config.MODULE_PACKAGE_PATHS = ["./demo/module_package1"]
    ioc_framework.inject_modules()

    # ioc_framework.delete_module_packages(["./demo/module_package1"])
    ioc_framework.add_module_packages(["./demo/module_package2"])

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    return fast_app


app = get_app()
