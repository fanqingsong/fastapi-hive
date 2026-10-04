from typing import Any

from fastapi import Depends
from starlette.requests import Request


class HiveRegistry:
    def __init__(self):
        self._items = {}

    def register(self, key: Any, instance: Any) -> None:
        self._items[key] = instance

    def get(self, key: Any) -> Any:
        return self._items[key]

    def has(self, key: Any) -> bool:
        return key in self._items


def DependsHive(key: Any):
    def _resolve(request: Request):
        request_hive = getattr(request.state, "hive", None)
        if request_hive is not None and request_hive.has(key):
            return request_hive.get(key)
        return request.app.state.hive.get(key)

    return Depends(_resolve)
