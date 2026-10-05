from example.endpoints_package2.heart_beat2.router.implement import router

from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


@endpoint(name="heart_beat2", order=1)
class EndpointHooksImpl(EndpointHooks):

    def startup(self):
        self.app.include_router(router, prefix="/api/hb2", tags=["heartbeat-v2"])
