

from fastapi import FastAPI
from loguru import logger
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer, EndpointMeta
from dependency_injector.wiring import Provide, inject
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


class EndpointRouterMounter:
    @inject
    def __init__(
            self,
            app: FastAPI,
            endpoint_container: EndpointContainer = Provide[DIContainer.endpoint_container],
            ioc_config: IoCConfig = Provide[DIContainer.ioc_config],
    ):
        logger.info("endpoint router mounter is initializing.")

        self._app = app
        self._endpoint_container = endpoint_container
        self._ioc_config = ioc_config

    def mount(self) -> None:
        logger.info("running endpoint router mounter.")

        app: FastAPI = self._app
        api_prefix = self._ioc_config.API_PREFIX

        hide_endpoint_container_in_api = self._ioc_config.HIDE_ENDPOINT_CONTAINER_IN_API
        hide_endpoint_in_api = self._ioc_config.HIDE_ENDPOINT_IN_API
        hide_endpoint_in_tag = self._ioc_config.HIDE_ENDPOINT_IN_TAG

        endpoints = self._endpoint_container.endpoints
        for one_endpoint_pkg_path, endpoint_instance in endpoints.items():
            logger.info(f"router mounting, endpoint name = {one_endpoint_pkg_path}")

            endpoint_instance: EndpointMeta = endpoint_instance

            imported_module_router = endpoint_instance.imported_module_router
            if not hasattr(imported_module_router, 'router'):
                logger.info("no router, cannot be mounted.")
                continue

            module_router = imported_module_router.router
            logger.info(module_router)
            container_name = endpoint_instance.container_name

            prefix = f"{api_prefix}"

            if not hide_endpoint_container_in_api:
                prefix = f"{prefix}/{container_name}"

            endpoint_name = one_endpoint_pkg_path.split('.')[-1]

            if not hide_endpoint_in_api:
                prefix = f"{prefix}/{endpoint_name}"

            tag = f"{container_name}"
            if not hide_endpoint_in_tag:
                tag = f"{tag}.{endpoint_name}"

            '''
            set container_name in url
            '''
            app.include_router(
                module_router,
                tags=[tag],
                prefix=prefix)

