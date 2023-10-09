
from fastapi_hive.ioc_framework.cornerstone_model import Cornerstone, CornerstoneMeta


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

