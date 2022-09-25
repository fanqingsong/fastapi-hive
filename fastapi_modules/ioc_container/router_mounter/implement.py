

from fastapi import FastAPI
from loguru import logger
from fastapi_modules.ioc_container.module_container import module_container
from fastapi import APIRouter


class RouterMounter:
    def __int__(self):
        logger.info("router mounter is starting.")

        self._app = None

    def bind_app(self, app: FastAPI):
        self._app = app

    def mount(self, api_prefix: str) -> None:
        app: FastAPI = self._app

        api_router = self._collect_router()
        app.include_router(api_router, prefix=api_prefix)

    def _collect_router(self) -> APIRouter:
        api_router = APIRouter()

        modules = module_container.modules
        for one_module, one_entity in modules.items():
            module_router = one_entity.router

            api_router.include_router(
                module_router,
                tags=[f"{one_module}"],
                prefix=f"/{one_module}")

        return api_router

    def unmount(self, api_prefix: str) -> None:
        pass
        # app: FastAPI = self._app

        '''
        fastapi don't support unmount router now.
        '''
        # api_router = APIRouter()
        # app.include_router(api_router, prefix=api_prefix)

