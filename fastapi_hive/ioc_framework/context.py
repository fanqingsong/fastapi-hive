from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from starlette.requests import Request

from fastapi_hive.ioc_framework.beans import BUILTIN_EXTRAS, BeanDefinition
from fastapi_hive.ioc_framework.registry import HiveRegistry, _call_if_request_dependency


class HiveContext:
    def __init__(self, app: Optional[FastAPI] = None):
        self.app = app
        self.definitions: List[BeanDefinition] = []
        self._by_key: Dict[Any, BeanDefinition] = {}
        self.app_cache = HiveRegistry()
        self._owners: Dict[type, Any] = {}
        self._creating: List[Any] = []
        self.autoconfigure_classes: List[type] = []

    def add_definitions(self, definitions: List[BeanDefinition]) -> None:
        self.definitions.extend(definitions)
        for item in definitions:
            existing = self._by_key.get(item.key)
            if existing is not None and existing is not item:
                if item.primary and not existing.primary:
                    self._by_key[item.key] = item
                    continue
                if existing.primary and not item.primary:
                    continue
                raise ValueError(
                    f"duplicate bean {item.key!r} without a single primary"
                )
            self._by_key[item.key] = item

    def has(self, key: Any) -> bool:
        return key in self._by_key or self.app_cache.has(key)

    def keys(self):
        return list(self._by_key)

    def get(self, key: Any, request: Optional[Request] = None, invoke_request_dep: bool = False):
        request_cache = None
        if request is not None:
            request_cache = getattr(request.state, "hive", None)
            if request_cache is not None and request_cache.has(key):
                value = request_cache.get(key)
                return _call_if_request_dependency(value, request) if invoke_request_dep else value
        if self.app_cache.has(key):
            value = self.app_cache.get(key)
            return _call_if_request_dependency(value, request) if invoke_request_dep and request else value
        if key not in self._by_key:
            raise KeyError(f"Hive dependency {key!r} is not registered")
        value = self._create(self._by_key[key], request)
        self._store(self._by_key[key], value, request)
        return _call_if_request_dependency(value, request) if invoke_request_dep and request else value

    def _store(self, definition: BeanDefinition, value: Any, request: Optional[Request]) -> None:
        if definition.scope == "transient":
            return
        if definition.scope == "request":
            if request is None:
                raise RuntimeError(f"request-scoped bean {definition.key!r} needs a request")
            cache = getattr(request.state, "hive", None)
            if cache is None:
                cache = HiveRegistry()
                request.state.hive = cache
            cache.register(definition.key, value)
            return
        self.app_cache.register(definition.key, value)

    def _create(self, definition: BeanDefinition, request: Optional[Request]):
        if definition.key in self._creating:
            cycle = self._creating + [definition.key]
            raise ValueError(f"circular hive dependency: {cycle}")
        self._creating.append(definition.key)
        try:
            from fastapi_hive.ioc_framework.decorators import (
                call_injected_sync,
                create_hook,
                resolve_params,
            )

            extras = {}
            if self.app is not None:
                extras[FastAPI] = self.app
            if request is not None:
                extras[Request] = request
            if definition.method_name:
                owner = self._owner(definition.owner_cls, extras, request)
                method = getattr(owner, definition.method_name)
                return call_injected_sync(method, self, request, extras)
            kwargs = resolve_params(definition.owner_cls.__init__, self, request, extras)
            return definition.owner_cls(**kwargs)
        finally:
            self._creating.pop()

    def _owner(self, cls: type, extras: dict, request: Optional[Request]):
        if cls in self._owners:
            return self._owners[cls]
        from fastapi_hive.ioc_framework.decorators import create_hook

        instance = create_hook(cls, self, extras, request)
        self._owners[cls] = instance
        return instance

    def validate(self) -> None:
        keys = set(self._by_key)
        graph = {}
        for definition in self.definitions:
            graph[definition.key] = [
                dep for dep in definition.deps
                if dep not in BUILTIN_EXTRAS
            ]
            for dep in graph[definition.key]:
                if dep not in keys:
                    raise KeyError(
                        f"Hive dependency {dep!r} required by {definition.key!r} is not registered"
                    )
        self._topo_sort(graph)

    def _topo_sort(self, graph: Dict[Any, List[Any]]) -> List[Any]:
        incoming = {key: 0 for key in graph}
        for key, deps in graph.items():
            for dep in deps:
                if dep in incoming:
                    incoming[key] += 1
        ready = [key for key, count in incoming.items() if count == 0]
        ordered = []
        while ready:
            key = ready.pop()
            ordered.append(key)
            for other, deps in graph.items():
                if key in deps:
                    incoming[other] -= 1
                    if incoming[other] == 0:
                        ready.append(other)
        if len(ordered) != len(graph):
            leftover = [key for key, count in incoming.items() if count > 0]
            raise ValueError(f"circular hive dependency: {leftover}")
        return ordered

    def refresh(self) -> None:
        self.validate()
        for definition in self.definitions:
            if definition.scope != "app" or definition.lazy:
                continue
            if self.app_cache.has(definition.key):
                continue
            self.get(definition.key)
