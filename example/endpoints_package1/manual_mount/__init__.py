from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from example.endpoints_package1.manual_mount.router.implement import router


@endpoint(name="manual_mount", order=30, profiles=["demo"], mount=False)
class ManualMountHooks(EndpointHooks):
    """ROUTER_MOUNT_AUTOMATED stays on. This module mounts itself."""

    def startup(self):
        self.app.include_router(router, prefix="/api/manual", tags=["manual-mount"])
        self.app.state.hive_lifecycle.append("manual.startup")
