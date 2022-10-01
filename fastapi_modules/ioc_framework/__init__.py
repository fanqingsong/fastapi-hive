
from fastapi_modules.ioc_framework.implement import IoCFramework
from fastapi_modules.ioc_framework.di_contiainer import DIContainer

di_container: DIContainer = DIContainer()
di_container.wire(
    modules=[
        "fastapi_modules.ioc_framework.implement",
        "fastapi_modules.ioc_framework.module_mounter",
        "fastapi_modules.ioc_framework.router_mounter",
    ]
)
