

from pydantic import BaseModel, Field
from typing import List, Dict


class IoCConfig(BaseModel):
    CORNERSTONE_PACKAGE_PATH: str = "./cornerstone"
    API_PREFIX: str = ""
    ENDPOINT_PACKAGE_PATHS: List[str] = ["./endpoints"]
    ACTIVE_PROFILES: List[str] = Field(default_factory=list)
    FEATURES: Dict = Field(default_factory=dict)
    AUTOCONFIGURE_ENABLED: bool = True
    AUTOCONFIGURE_IMPORTS: List[str] = Field(default_factory=list)
    AUTOCONFIGURE_EXCLUDE: List[str] = Field(default_factory=list)
    ROUTER_MOUNT_AUTOMATED: bool = True
    HIDE_ENDPOINT_CONTAINER_IN_API: bool = False
    HIDE_ENDPOINT_IN_API: bool = False
    HIDE_ENDPOINT_IN_TAG: bool = False

