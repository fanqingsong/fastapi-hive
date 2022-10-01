
from fastapi_hive.ioc_framework.module_container import ModuleContainer
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from dependency_injector import containers, providers


class DIContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    module_container = providers.Singleton(
        ModuleContainer
    )

    ioc_config = providers.Singleton(
        IoCConfig
    )
