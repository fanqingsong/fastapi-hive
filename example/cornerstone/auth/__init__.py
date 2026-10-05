from fastapi_hive.ioc_framework.decorators import autoconfigure, provides
from example.cornerstone.auth.implement import validate_http_request


@autoconfigure(name="hive.auth", order=100)
class AuthAuto:

    @provides("auth.ok")
    def checker(self):
        return validate_http_request
