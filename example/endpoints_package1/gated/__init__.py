from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from example.endpoints_package1.gated.router.implement import router


@endpoint(name="gated", enabled_when="missing_flag", mount=False)
class GatedHooks(EndpointHooks):
    """enabled_when misses FEATURES, so startup never mounts it."""

    def startup(self):
        self.app.state.hive_lifecycle.append("gated.startup")
        self.app.include_router(router, prefix="/api/gated", tags=["gated"])
