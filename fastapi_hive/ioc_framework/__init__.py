
from fastapi_hive.ioc_framework.implement import IoCFramework
from fastapi_hive.ioc_framework.di_contiainer import DIContainer


__all__ = ["IoCFramework"]


di_container: DIContainer = DIContainer()
di_container.wire(
    modules=[
        "fastapi_hive.ioc_framework.endpoint_container_mounter.implement",
        "fastapi_hive.ioc_framework.endpoint_router_mounter.implement",
        "fastapi_hive.ioc_framework.cornerstone_hook_caller.implement",
        "fastapi_hive.ioc_framework.implement",
    ]
)
