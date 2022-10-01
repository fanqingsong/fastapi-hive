

from fastapi import FastAPI
from loguru import logger
from demo.core.config import (APP_NAME, APP_VERSION, API_PREFIX,
                                         IS_DEBUG)

from fastapi_hive.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    ioc_framework = IoCFramework(fast_app)
    ioc_framework.config.API_PREFIX = API_PREFIX
    ioc_framework.config.MODULE_PACKAGE_PATHS = ["./demo/package1", "./demo/package2"]
    # logger.info("-----------------------------------------------------")
    # logger.info(dir(ioc_framework))
    # logger.info(dir(ioc_framework.config))
    ioc_framework.config.HIDE_PACKAGE_IN_URL = True
    ioc_framework.init_modules()

    # ioc_framework.delete_modules_by_packages(["./demo/package1"])
    # ioc_framework.add_modules_by_packages(["./demo/package2"])

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    return fast_app


app = get_app()
