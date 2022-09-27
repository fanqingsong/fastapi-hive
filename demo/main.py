

from fastapi import FastAPI
from loguru import logger
from demo.core.config import (APP_NAME, APP_VERSION, API_PREFIX,
                                         IS_DEBUG)

from fastapi_modules.ioc_framework import ioc_framework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    ioc_framework\
        .bind_app(fast_app)\
        .set_params({
            "API_PREFIX": API_PREFIX,
            "MODULE_PACKAGE_PATHS": ["./demo/modules"]
        })\
        .init()

    # ioc_framework.delete_module_packages(["./demo/modules"])
    ioc_framework.add_module_packages(["./demo/modules_another"])

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    return fast_app


app = get_app()
