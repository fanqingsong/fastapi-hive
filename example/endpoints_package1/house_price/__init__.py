from example.endpoints_package1.house_price.router.implement import router
from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


@endpoint(name="house_price")
class EndpointHooksImpl(EndpointHooks):

    def startup(self):
        self.app.include_router(router, prefix="/api/house_price", tags=["house_price"])
