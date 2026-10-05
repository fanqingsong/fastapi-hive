
from example.endpoints_package2.heart_beat2.router.implement import router

from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


@endpoint(name="heart_beat2", order=1, prefix="/api/hb2", tags=["heartbeat-v2"])
class EndpointHooksImpl(EndpointHooks):

    def startup(self):
        print("heart_beat2 routers collected by IoC:")
        for binding in self.endpoint.routers:
            print(
                f"  name={binding.name} order={binding.order} "
                f"prefix={binding.mount.prefix} tags={binding.mount.tags} "
                f"explicit={binding.mount.explicit}"
            )
