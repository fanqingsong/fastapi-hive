
from fastapi import FastAPI
from fastapi_modules.core.config import (API_PREFIX)


from fastapi_modules.ioc_container.router import setup_router
from fastapi_modules.ioc_container.service import setup_service, teardown_service


def setup(app: FastAPI) -> None:
    setup_service(app)

    api_router = setup_router()
    app.include_router(api_router, prefix=API_PREFIX)


def teardown(app: FastAPI) -> None:
    teardown_service(app)
