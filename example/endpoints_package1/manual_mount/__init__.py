from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from example.endpoints_package1.manual_mount.router.implement import router


@endpoint(name="manual_mount", order=30, profiles=["demo"])
class ManualMountHooks(EndpointHooks):
    """This module mounts its router in startup."""

    def startup(self):
        self.app.include_router(router, prefix="/api/manual", tags=["manual-mount"])
        self.app.state.hive_lifecycle.append("manual.startup")
