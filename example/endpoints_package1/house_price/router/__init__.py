
from example.endpoints_package1.house_price.router.implement import router

from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.decorators import endpoint


@endpoint(name="house_price")
class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def startup(self):
        print("call pre startup from EndpointHooksImpl (router)!!!")
        print(self.app)




