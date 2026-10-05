from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks

from example.endpoints_package2.house_price2.router.implement import router


@endpoint(name="house_price2")
class EndpointHooksImpl(EndpointHooks):

    def startup(self):
        print("call pre startup from EndpointHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)
        self.app.include_router(
            router, prefix="/api/house_price2", tags=["house_price2"]
        )

    def shutdown(self):
        print("call pre shutdown from EndpointHooksImpl!!!")
