
from fastapi_hive.ioc_framework.implement import IoCFramework
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.decorators import cornerstone, endpoint, provides, request_provides
from fastapi_hive.ioc_framework.registry import DependsHive, HiveRegistry


__all__ = [
    "IoCFramework",
    "cornerstone",
    "endpoint",
    "provides",
    "request_provides",
    "DependsHive",
    "HiveRegistry",
]


di_container: DIContainer = DIContainer()
di_container.wire(
    modules=[
        "fastapi_hive.ioc_framework.endpoint_router_mounter.implement",
        "fastapi_hive.ioc_framework.cornerstone_hooks.implement",
        "fastapi_hive.ioc_framework.endpoint_hooks.implement",
        "fastapi_hive.ioc_framework.implement",
    ]
)

