from fastapi import FastAPI

from fastapi_hive.ioc_framework.decorators import endpoint, provides
from fastapi_hive.ioc_framework.endpoint_container import EndpointMeta
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks


@endpoint(name="showcase", order=5, profiles=["demo"], enabled_when="audit")
class ShowcaseHooks(EndpointHooks):
    """Async startup/shutdown. user_message is a scanned bean, so the
    on_missing starter in beans.py yields to it.
    """

    @provides("showcase.user_message")
    def user_message(self):
        return "from-user"

    async def startup(self, app: FastAPI, endpoint: EndpointMeta):
        app.state.hive_lifecycle.append("showcase.startup")
        app.state.showcase_endpoint_name = endpoint.name
        app.state.showcase_router_count = len(endpoint.routers)

    async def shutdown(self):
        self.app.state.hive_lifecycle.append("showcase.shutdown")
