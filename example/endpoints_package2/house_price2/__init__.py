
from fastapi_hive.ioc_framework.decorators import endpoint
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


@endpoint(name="house_price2")
class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def startup(self):
        print("call pre startup from EndpointHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)

    def shutdown(self):
        print("call pre shutdown from EndpointHooksImpl!!!")
