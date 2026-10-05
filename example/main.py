
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
from example.cornerstone.config import (APP_NAME, APP_VERSION, IS_DEBUG)

from fastapi_hive.ioc_framework import IoCFramework


def get_app() -> FastAPI:
    logger.info("app is starting.")

    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    IoCFramework.bootstrap(fast_app)

    @fast_app.get("/")
    def get_root():
        return "Go to docs URL to look up API: http://localhost:8000/docs"

    @fast_app.get("/hive/routers")
    def list_collected_routers():
        items = []
        for key, slot in fast_app.state.endpoints.items():
            meta = slot.get("__endpoint__")
            if meta is None:
                continue
            for binding in getattr(meta, "routers", []):
                items.append({
                    "endpoint": key,
                    "name": binding.name,
                    "order": binding.order,
                    "skip": binding.mount.skip,
                    "prefix": binding.mount.prefix,
                    "tags": binding.mount.tags,
                    "explicit": binding.mount.explicit,
                    "paths": [getattr(route, "path", None) for route in binding.router.routes],
                })
        return items

    return fast_app


app = get_app()
