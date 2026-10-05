
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
from fastapi_hive.ioc_framework.decorators import cornerstone, provides
from example.cornerstone.auth.implement import validate_request


@cornerstone(name="auth", order=100)
class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self):
        super(CornerstoneHooksImpl, self).__init__()

    @provides("auth.validate_request")
    def pre_endpoint_startup(self):
        print("call pre startup from CornerstoneHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)
        return validate_request

    def post_endpoint_startup(self):
        print("call post startup from CornerstoneHooksImpl!!!")

    def pre_endpoint_shutdown(self):
        print("call pre shutdown from CornerstoneHooksImpl!!!")

    def post_endpoint_shutdown(self):
        print("call pre shutdown from CornerstoneHooksImpl!!!")

    def pre_endpoint_call(self):
        pass

    def post_endpoint_call(self):
        pass


@cornerstone(name="auth", order=100)
class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self):
        super(CornerstoneAsyncHooksImpl, self).__init__()

    async def pre_endpoint_startup(self):
        print("call pre startup from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_startup(self):
        print("call post startup from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_shutdown(self):
        print("call pre shutdown from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_shutdown(self):
        print("call pre shutdown from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_call(self):
        pass

    async def post_endpoint_call(self):
        pass
