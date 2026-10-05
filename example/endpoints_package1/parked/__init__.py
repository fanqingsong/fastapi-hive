from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from example.endpoints_package1.parked.router.implement import router


@endpoint(name="parked", profiles=["never"], mount=False)
class ParkedHooks(EndpointHooks):
    """profiles does not overlap ACTIVE_PROFILES, so startup never mounts it."""

    def startup(self):
        self.app.state.hive_lifecycle.append("parked.startup")
        self.app.include_router(router, prefix="/api/parked", tags=["parked"])
