

from fastapi import FastAPI

from fastapi_skeleton.core.config import (API_PREFIX, APP_NAME, APP_VERSION,
                                          IS_DEBUG)

from fastapi_skeleton.modules_container.service import (start_app_handler,
                                                        stop_app_handler)
from fastapi_skeleton.modules_container.router import setup_router


def get_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)

    api_router = setup_router()
    fast_app.include_router(api_router, prefix=API_PREFIX)

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app


app = get_app()
