

from pydantic import BaseModel
from typing import List, Callable


class IoCConfig(BaseModel):
    CORNERSTONE_PACKAGE_PATHS: List[str] = ["./cornerstone"]
    API_PREFIX: str = ""
    ENDPOINT_PACKAGE_PATHS: List[str] = ["./example/endpoints_package1"]
    HIDE_PACKAGE_IN_URL: bool = False
    HIDE_MODULE_IN_URL: bool = False
    PRE_ENDPOINT_SETUP: Callable = None
    POST_ENDPOINT_SETUP: Callable = None
    PRE_ENDPOINT_TEARDOWN: Callable = None
    POST_ENDPOINT_TEARDOWN: Callable = None
    ASYNC_PRE_ENDPOINT_SETUP: Callable = None
    ASYNC_POST_ENDPOINT_SETUP: Callable = None
    ASYNC_PRE_ENDPOINT_TEARDOWN: Callable = None
    ASYNC_POST_ENDPOINT_TEARDOWN: Callable = None

