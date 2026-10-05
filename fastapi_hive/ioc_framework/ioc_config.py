

from pydantic import BaseModel, Field
from typing import List, Dict


class IoCConfig(BaseModel):
    FOUNDATION_PACKAGE_PATH: str = "./foundation"
    API_PREFIX: str = ""
    ENDPOINT_PACKAGE_PATHS: List[str] = ["./endpoints"]
    ACTIVE_PROFILES: List[str] = Field(default_factory=list)
    FEATURES: Dict = Field(default_factory=dict)
    AUTOCONFIGURE_ENABLED: bool = True
    AUTOCONFIGURE_IMPORTS: List[str] = Field(default_factory=list)
    AUTOCONFIGURE_EXCLUDE: List[str] = Field(default_factory=list)
    RUNNER_IMPORTS: List[str] = Field(default_factory=list)

