

from pydantic import BaseModel, Field
from typing import List, Callable, Dict


class IoCConfig(BaseModel):
    CORNERSTONE_PACKAGE_PATH: str = "./cornerstone"
    API_PREFIX: str = ""
    ENDPOINT_PACKAGE_PATHS: List[str] = ["./endpoints"]
    ACTIVE_PROFILES: List[str] = Field(default_factory=list)
    FEATURES: Dict = Field(default_factory=dict)
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

