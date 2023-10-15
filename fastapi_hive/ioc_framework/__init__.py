
from fastapi_hive.ioc_framework.implement import IoCFramework
from fastapi_hive.ioc_framework.di_contiainer import DIContainer


__all__ = ["IoCFramework"]


di_container: DIContainer = DIContainer()
di_container.wire(
    modules=[
        "fastapi_hive.ioc_framework.endpoint_router_mounter.implement",
        "fastapi_hive.ioc_framework.cornerstone_hooks.implement",
        "fastapi_hive.ioc_framework.endpoint_hooks.implement",
        "fastapi_hive.ioc_framework.implement",
    ]
)

