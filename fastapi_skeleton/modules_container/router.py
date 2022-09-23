

from typing import Callable

from fastapi import FastAPI
from loguru import logger

from fastapi_skeleton.modules_container.discover import discover
from fastapi import APIRouter


def setup_router() -> APIRouter:
    api_router = APIRouter()

    modules = discover.modules
    for one_module, one_entity in modules.items():
        router = one_entity["router"]
        module_router = router.api_router

        api_router.include_router(module_router, tags=[f"{one_module}"], prefix=f"/{one_module}")

    return api_router


