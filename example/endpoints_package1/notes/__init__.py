from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from example.endpoints_package1.notes.router.implement import router


@endpoint(name="notes")
class EndpointHooksImpl(EndpointHooks):

    def startup(self):
        self.app.include_router(router, prefix="/api/notes", tags=["notes"])
