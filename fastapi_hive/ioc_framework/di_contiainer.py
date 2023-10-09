
from fastapi_hive.ioc_framework.endpoint_container import EndpointContainer
from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from dependency_injector import containers, providers


class DIContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    cornerstone_container = providers.Singleton(
        CornerstoneContainer
    )

    endpoint_container = providers.Singleton(
        EndpointContainer
    )

    ioc_config = providers.Singleton(
        IoCConfig
    )
