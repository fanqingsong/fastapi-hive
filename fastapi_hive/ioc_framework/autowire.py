import inspect
from typing import Any, Callable, get_origin, get_type_hints

from fastapi import FastAPI
from starlette.requests import Request

from fastapi_hive.ioc_framework.beans import unwrap_hint
from fastapi_hive.ioc_framework.registry import Inject

try:
    from pydantic import BaseModel
except ImportError:  # pragma: no cover
    BaseModel = None


_PRIMITIVES = {int, str, float, bool, bytes, type(None), list, dict, tuple, set}


def _is_pydantic(hint: Any) -> bool:
    return (
        BaseModel is not None
        and inspect.isclass(hint)
        and issubclass(hint, BaseModel)
    )


def should_autowire(hint: Any, param: inspect.Parameter, context) -> bool:
    if hint is None or hint in _PRIMITIVES or hint in {Request, FastAPI}:
        return False
    if get_origin(hint) in {list, dict, tuple, set}:
        return False
    key = unwrap_hint(hint)
    if key in _PRIMITIVES or _is_pydantic(key):
        return False
    if param.default is not inspect.Parameter.empty:
        return False
    return context.has(key)


def apply_autowire(func: Callable, context) -> Callable:
    try:
        hints = get_type_hints(func)
    except Exception:
        return func
    signature = inspect.signature(func)
    parameters = []
    changed = False
    for name, param in signature.parameters.items():
        hint = hints.get(name)
        if should_autowire(hint, param, context):
            parameters.append(param.replace(default=Inject(unwrap_hint(hint))))
            changed = True
        else:
            parameters.append(param)
    if not changed:
        return func
    func.__signature__ = signature.replace(parameters=parameters)
    return func


def autowire_router(router, context) -> None:
    for route in getattr(router, "routes", []):
        endpoint = getattr(route, "endpoint", None)
        if endpoint is None:
            continue
        apply_autowire(endpoint, context)
