

from pydantic import BaseModel
from typing import Callable, Dict, List


class IoCConfig(BaseModel):
    API_PREFIX: str = ""
    MODULE_PACKAGE_PATHS: List[str] = ["./demo/package1"]
    HIDE_PACKAGE_IN_URL: bool = True
