
from fastapi_hive.ioc_framework.cornerstone_model import Cornerstone, CornerstoneAsync


class CornerstoneImpl(Cornerstone):

    def __init__(self):
        super(CornerstoneImpl, self).__init__()

    def pre_setup(self):
        print("call pre setup from cornerstone!!!")

    def post_setup(self):
        print("call post setup from cornerstone!!!")

    def pre_teardown(self):
        print("call pre teardown from cornerstone!!!")

    def post_teardown(self):
        print("call pre teardown from cornerstone!!!")


class CornerstoneAsyncImpl(Cornerstone):

    def __init__(self):
        super(CornerstoneAsyncImpl, self).__init__()

    async def pre_setup(self):
        print("call pre setup from cornerstone async!!!")

    async def post_setup(self):
        print("call post setup from cornerstone async!!!")

    async def pre_teardown(self):
        print("call pre teardown from cornerstone async!!!")

    async def post_teardown(self):
        print("call pre teardown from cornerstone async!!!")

