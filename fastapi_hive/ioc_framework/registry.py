from typing import Any, Optional

from fastapi import Depends
from starlette.requests import Request


class HiveRegistry:
    def __init__(self):
        self._items = {}

    def register(self, key: Any, instance: Any) -> None:
        self._items[key] = instance

    def get(self, key: Any) -> Any:
        if key not in self._items:
            raise KeyError(f"Hive dependency {key!r} is not registered")
        return self._items[key]

    def has(self, key: Any) -> bool:
        return key in self._items

    def resolve(self, key: Any) -> Any:
        return self.get(key)


def resolve(key: Any, app_registry, request_registry=None):
    if request_registry is not None and request_registry.has(key):
        return request_registry.get(key)
    if app_registry is not None and hasattr(app_registry, "get") and (
        app_registry.has(key) if hasattr(app_registry, "has") else True
    ):
        if hasattr(app_registry, "has") and not app_registry.has(key):
            raise KeyError(f"Hive dependency {key!r} is not registered")
        return app_registry.get(key)
    raise KeyError(f"Hive dependency {key!r} is not registered")


def _call_if_request_dependency(value: Any, request: Request):
    import inspect
    from typing import get_type_hints

    if not callable(value) or isinstance(value, type):
        return value
    try:
        hints = get_type_hints(value)
        parameters = [
            param
            for param in inspect.signature(value).parameters.values()
            if param.kind in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]
    except (TypeError, ValueError):
        return value
    if len(parameters) == 1 and hints.get(parameters[0].name) is Request:
        return value(request)
    return value


class HiveKey:
    def __init__(self, key: Any):
        self.key = key

    def __call__(self, request: Request):
        hive = getattr(request.app.state, "hive", None)
        if hive is not None and hasattr(hive, "get") and hasattr(hive, "definitions"):
            return hive.get(self.key, request, invoke_request_dep=True)
        request_hive = getattr(request.state, "hive", None)
        app_hive = getattr(request.app.state, "hive", None)
        cache = app_hive.app_cache if hasattr(app_hive, "app_cache") else app_hive
        value = resolve(self.key, cache, request_hive)
        return _call_if_request_dependency(value, request)


def Inject(key: Any):
    return Depends(HiveKey(key))
