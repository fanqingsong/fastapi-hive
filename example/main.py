
import sys
from pathlib import Path

# Prefer this repository over a previously installed PyPI copy.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_repo_root = str(_REPO_ROOT)
if _repo_root in sys.path:
    sys.path.remove(_repo_root)
sys.path.insert(0, _repo_root)

from fastapi import FastAPI
from loguru import logger
from example.foundation.config import (APP_NAME, APP_VERSION, IS_DEBUG)

from fastapi_hive.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    IoCFramework.bootstrap(
        fast_app,
        settings={
            "api_prefix": "/api",
            "foundation_package_path": "./foundation",
            "endpoint_package_paths": [
                "./endpoints_package1",
                "./endpoints_package2",
            ],
            "active_profiles": ["demo"],
            "features": {"db": True, "audit": True},
            "autoconfigure": {
                "enabled": True,
                "imports": ["example.starters.imported_auto:ImportedAuto"],
                "exclude": ["showcase.skipped"],
            },
            "runners": {
                "imports": [
                    "example.starters.seed_runner:SeedDataRunner",
                    "example.starters.seed_runner:NeverSeedRunner",
                ],
            },
        },
    )

    @fast_app.get("/")
    def get_root():
        return {
            "docs": "/docs",
            "feature_tour": "/api/showcase/tour",
            "manual_mount": "/api/manual/ping",
            "mounted_routers": "/hive/routers",
        }

    @fast_app.get("/hive/routers")
    def list_mounted_routers():
        items = []
        for path, operations in fast_app.openapi().get("paths", {}).items():
            methods = sorted(
                name.upper()
                for name in operations
                if name not in {"parameters", "summary", "description", "servers"}
            )
            items.append({"path": path, "methods": methods})
        return items

    return fast_app


app = get_app()
