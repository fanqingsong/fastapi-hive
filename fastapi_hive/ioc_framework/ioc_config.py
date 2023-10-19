

from pydantic import BaseModel
from typing import List, Callable


class IoCConfig(BaseModel):
    CORNERSTONE_PACKAGE_PATH: str = "./cornerstone"
    API_PREFIX: str = ""
    ENDPOINT_PACKAGE_PATHS: List[str] = ["./example/endpoints_package1"]
    ROUTER_MOUNT_AUTOMATED: bool = True
    HIDE_ENDPOINT_CONTAINER_IN_API: bool = False
    HIDE_ENDPOINT_IN_API: bool = False
    HIDE_ENDPOINT_IN_TAG: bool = False
    PRE_ENDPOINT_SETUP: Callable = None
    POST_ENDPOINT_SETUP: Callable = None
    PRE_ENDPOINT_TEARDOWN: Callable = None
    POST_ENDPOINT_TEARDOWN: Callable = None
    ASYNC_PRE_ENDPOINT_SETUP: Callable = None
    ASYNC_POST_ENDPOINT_SETUP: Callable = None
    ASYNC_PRE_ENDPOINT_TEARDOWN: Callable = None
    ASYNC_POST_ENDPOINT_TEARDOWN: Callable = None

