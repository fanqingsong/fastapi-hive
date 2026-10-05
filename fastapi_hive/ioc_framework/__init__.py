from fastapi_hive.ioc_framework.implement import IoCFramework
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.decorators import (
    autoconfigure,
    component,
    conditional,
    cornerstone,
    endpoint,
    provides,
    Qualifier,
)
from fastapi_hive.ioc_framework.registry import Inject, HiveRegistry
from fastapi_hive.ioc_framework.context import HiveContext


__all__ = [
    "IoCFramework",
    "cornerstone",
    "endpoint",
    "provides",
    "component",
    "autoconfigure",
    "conditional",
    "Qualifier",
    "Inject",
    "HiveRegistry",
    "HiveContext",
]


di_container: DIContainer = DIContainer()
di_container.wire(
    modules=[
        "fastapi_hive.ioc_framework.cornerstone_hooks.implement",
        "fastapi_hive.ioc_framework.endpoint_hooks.implement",
        "fastapi_hive.ioc_framework.implement",
    ]
)
