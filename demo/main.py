

from fastapi import FastAPI
from loguru import logger
from demo.cornerstone.config import (APP_NAME, APP_VERSION, API_PREFIX,
                                     IS_DEBUG)

from fastapi_hive.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    def hive_pre_setup():
        logger.info("------ call pre setup -------")

    def hive_post_setup():
        logger.info("------ call post setup -------")

    async def hive_async_pre_setup():
        logger.info("------ call async pre setup -------")

    async def hive_async_post_setup():
        logger.info("------ call async post setup -------")

    ioc_framework = IoCFramework(fast_app)
    ioc_framework.config.CORNERSTONE_PACKAGE_PATHS = ["./demo/cornerstone/"]

    ioc_framework.config.API_PREFIX = API_PREFIX
    ioc_framework.config.MODULE_PACKAGE_PATHS = ["./demo/xxx_endpoint", "./demo/yyy_endpoint"]
    # logger.info("-----------------------------------------------------")
    # logger.info(dir(ioc_framework))
    # logger.info(dir(ioc_framework.config))
    ioc_framework.config.HIDE_PACKAGE_IN_URL = False
    ioc_framework.config.HIDE_MODULE_IN_URL = False
    ioc_framework.config.PRE_SETUP = hive_pre_setup
    ioc_framework.config.POST_SETUP = hive_post_setup
    ioc_framework.config.ASYNC_PRE_SETUP = hive_async_pre_setup
    ioc_framework.config.ASYNC_POST_SETUP = hive_async_post_setup

    ioc_framework.init_modules()

    # ioc_framework.delete_modules_by_packages(["./demo/xxx_endpoint"])
    # ioc_framework.add_modules_by_packages(["./demo/yyy_endpoint"])

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    return fast_app


app = get_app()
