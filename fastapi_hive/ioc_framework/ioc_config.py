

from pydantic import BaseModel
from typing import List


class IoCConfig(BaseModel):
    API_PREFIX: str = ""
    MODULE_PACKAGE_PATHS: List[str] = ["./demo/package1"]
    HIDE_PACKAGE_IN_URL: bool = False
    HIDE_MODULE_IN_URL: bool = False
