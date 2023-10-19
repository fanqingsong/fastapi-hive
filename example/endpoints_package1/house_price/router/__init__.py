
from example.endpoints_package1.house_price.router.implement import router

from fastapi import FastAPI
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


class EndpointHooksImpl(EndpointHooks):

    def __init__(self):
        super(EndpointHooksImpl, self).__init__()

    def setup(self):
        print("call pre setup from EndpointHooksImpl (service)!!!")

        app: FastAPI = self.app

        app.include_router(router, tags=["house price"], prefix=f"/v1/house_price1")




