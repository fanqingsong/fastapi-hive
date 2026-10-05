from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from example.endpoints_package1.heart_beat.router.implement import router


@endpoint(name="heart_beat")
class EndpointHooksImpl(EndpointHooks):

    def startup(self):
        self.app.include_router(router, prefix="/api/heart_beat", tags=["heart_beat"])
