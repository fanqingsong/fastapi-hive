

from pydantic import BaseModel
from typing import List, Callable


class IoCConfig(BaseModel):
    API_PREFIX: str = ""
    MODULE_PACKAGE_PATHS: List[str] = ["./demo/package1"]
    HIDE_PACKAGE_IN_URL: bool = False
    HIDE_MODULE_IN_URL: bool = False
    PRE_SETUP: Callable = None
    POST_SETUP: Callable = None
    PRE_TEARDOWN: Callable = None
    POST_TEARDOWN: Callable = None
    ASYNC_PRE_SETUP: Callable = None
    ASYNC_POST_SETUP: Callable = None
    ASYNC_PRE_TEARDOWN: Callable = None
    ASYNC_POST_TEARDOWN: Callable = None

