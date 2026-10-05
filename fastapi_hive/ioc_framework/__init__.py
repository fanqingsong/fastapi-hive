from fastapi_hive.ioc_framework.implement import IoCFramework
from fastapi_hive.ioc_framework.di_contiainer import DIContainer
from fastapi_hive.ioc_framework.decorators import (
    autoconfigure,
    component,
    conditional,
    foundation,
    endpoint,
    provides,
    Qualifier,
    runner,
)
from fastapi_hive.ioc_framework.registry import Inject, HiveRegistry
from fastapi_hive.ioc_framework.context import HiveContext
from fastapi_hive.ioc_framework.application_runner import ApplicationRunner


__all__ = [
    "IoCFramework",
    "foundation",
    "endpoint",
    "runner",
    "provides",
    "component",
    "autoconfigure",
    "conditional",
    "Qualifier",
    "Inject",
    "HiveRegistry",
    "HiveContext",
    "ApplicationRunner",
]


di_container: DIContainer = DIContainer()
di_container.wire(
    modules=[
        "fastapi_hive.ioc_framework.foundation_hooks.implement",
        "fastapi_hive.ioc_framework.endpoint_hooks.implement",
        "fastapi_hive.ioc_framework.implement",
    ]
)
