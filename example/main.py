

from fastapi import FastAPI
from loguru import logger
from example.cornerstone.config import (APP_NAME, APP_VERSION, API_PREFIX,
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
    ioc_framework.config.CORNERSTONE_PACKAGE_PATH = "./example/cornerstone/"

    ioc_framework.config.API_PREFIX = API_PREFIX
    ioc_framework.config.ENDPOINT_PACKAGE_PATHS = ["./example/endpoints_package1", "./example/endpoints_package2"]
    ioc_framework.config.ROUTER_MOUNT_AUTOMATED = True
    ioc_framework.config.HIDE_ENDPOINT_CONTAINER_IN_API = True
    ioc_framework.config.HIDE_ENDPOINT_IN_API = False
    ioc_framework.config.HIDE_ENDPOINT_IN_TAG = True
    ioc_framework.config.PRE_ENDPOINT_SETUP = hive_pre_setup
    ioc_framework.config.POST_ENDPOINT_SETUP = hive_post_setup
    ioc_framework.config.ASYNC_PRE_ENDPOINT_SETUP = hive_async_pre_setup
    ioc_framework.config.ASYNC_POST_ENDPOINT_SETUP = hive_async_post_setup

    ioc_framework.init_modules()

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    return fast_app


app = get_app()
