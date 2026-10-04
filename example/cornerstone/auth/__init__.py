
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks, CornerstoneAsyncHooks
from fastapi_hive.ioc_framework.decorators import cornerstone, provides
from example.cornerstone.auth.implement import validate_request


@cornerstone(name="auth", order=100)
class CornerstoneHooksImpl(CornerstoneHooks):

    def __init__(self):
        super(CornerstoneHooksImpl, self).__init__()

    @provides("auth.validate_request")
    def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneHooksImpl!!!")
        print("---- get fastapi app ------")
        print(self.app)
        return validate_request

    def post_endpoint_setup(self):
        print("call post setup from CornerstoneHooksImpl!!!")

    def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")

    def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneHooksImpl!!!")

    def pre_endpoint_call(self):
        pass

    def post_endpoint_call(self):
        pass


@cornerstone(name="auth", order=100)
class CornerstoneAsyncHooksImpl(CornerstoneAsyncHooks):

    def __init__(self):
        super(CornerstoneAsyncHooksImpl, self).__init__()

    async def pre_endpoint_setup(self):
        print("call pre setup from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_setup(self):
        print("call post setup from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

    async def post_endpoint_teardown(self):
        print("call pre teardown from CornerstoneAsyncHooksImpl!!!")

    async def pre_endpoint_call(self):
        pass

    async def post_endpoint_call(self):
        pass
