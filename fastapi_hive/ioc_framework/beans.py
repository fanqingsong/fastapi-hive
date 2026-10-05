import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, get_args, get_origin, get_type_hints

from fastapi import FastAPI
from starlette.requests import Request


BUILTIN_EXTRAS = {FastAPI, Request}


@dataclass
class BeanCondition:
    on_import: Optional[str] = None
    on_missing: Optional[Any] = None
    on_bean: Optional[Any] = None
    enabled_when: Optional[str] = None
    profiles: Optional[List[str]] = None
    on_property: Optional[str] = None


@dataclass
class BeanDefinition:
    key: Any
    owner_cls: Optional[type]
    method_name: Optional[str]
    deps: List[Any]
    scope: str = "app"
    source: str = "scan"
    conditions: BeanCondition = field(default_factory=BeanCondition)
    autoconfigure_name: Optional[str] = None
    order: int = 0
    after: List[str] = field(default_factory=list)
    before: List[str] = field(default_factory=list)
    lazy: bool = False
    primary: bool = False


def merge_conditions(base: Optional[BeanCondition], extra: Optional[BeanCondition]) -> BeanCondition:
    left = base or BeanCondition()
    right = extra or BeanCondition()
    return BeanCondition(
        on_import=right.on_import or left.on_import,
        on_missing=right.on_missing if right.on_missing is not None else left.on_missing,
        on_bean=right.on_bean if right.on_bean is not None else left.on_bean,
        enabled_when=right.enabled_when or left.enabled_when,
        profiles=right.profiles or left.profiles,
        on_property=right.on_property or left.on_property,
    )


def inject_key_from_default(default: Any) -> Any:
    from fastapi.params import Depends as DependsParam
    from fastapi_hive.ioc_framework.registry import HiveKey

    if isinstance(default, DependsParam) and isinstance(default.dependency, HiveKey):
        return default.dependency.key
    return None


def qualifier_from_hint(hint: Any) -> Any:
    origin = get_origin(hint)
    args = get_args(hint)
    if origin is None or not args:
        return None
    from fastapi_hive.ioc_framework.decorators import Qualifier

    for item in args[1:]:
        if isinstance(item, Qualifier):
            return item.name
    return None


def unwrap_hint(hint: Any) -> Any:
    origin = get_origin(hint)
    args = get_args(hint)
    if origin is None:
        return hint
    from typing import Union

    if origin is Union:
        non_none = [item for item in args if item is not type(None)]
        if len(non_none) == 1:
            return unwrap_hint(non_none[0])
    if args:
        qualified = qualifier_from_hint(hint)
        if qualified is not None:
            return qualified
        return unwrap_hint(args[0])
    return hint


def infer_deps(func: Callable) -> List[Any]:
    try:
        hints = get_type_hints(func, include_extras=True)
    except Exception:
        try:
            hints = get_type_hints(func)
        except Exception:
            hints = {}
    deps = []
    for name, param in inspect.signature(func).parameters.items():
        if name == "self":
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        key = inject_key_from_default(param.default)
        if key is not None:
            deps.append(key)
            continue
        hint = hints.get(name)
        if hint is None:
            continue
        key = qualifier_from_hint(hint) or unwrap_hint(hint)
        if key in BUILTIN_EXTRAS:
            continue
        if inspect.isclass(key) and key.__module__ in (
            "fastapi_hive.ioc_framework.cornerstone_container.implement",
            "fastapi_hive.ioc_framework.endpoint_container.implement",
        ):
            continue
        deps.append(key)
    return deps


def definition_from_component(cls: type, source: str = "scan") -> BeanDefinition:
    meta = cls.__hive_component__
    key = meta["key"]
    scope = meta["scope"]
    conditions = getattr(cls, "__hive_conditional__", BeanCondition())
    auto = getattr(cls, "__hive_autoconfigure__", None) or {}
    return BeanDefinition(
        key=key,
        owner_cls=cls,
        method_name=None,
        deps=infer_deps(cls.__init__),
        scope=scope,
        source=source,
        conditions=merge_conditions(auto.get("conditions"), conditions),
        autoconfigure_name=auto.get("name"),
        order=auto.get("order", 0),
        after=list(auto.get("after") or []),
        before=list(auto.get("before") or []),
        lazy=scope == "request" or bool(meta.get("lazy")),
        primary=bool(meta.get("primary")),
    )


def definitions_from_class(cls: type, source: str) -> List[BeanDefinition]:
    from fastapi_hive.ioc_framework.decorators import collect_providers

    auto = getattr(cls, "__hive_autoconfigure__", None) or {}
    class_cond = getattr(cls, "__hive_conditional__", None)
    if auto:
        class_cond = merge_conditions(auto.get("conditions"), class_cond)
        source = "autoconfigure"
    defs = []
    for spec in collect_providers(cls):
        func = getattr(cls, spec.name)
        raw = getattr(func, "__func__", func)
        method_cond = getattr(raw, "__hive_conditional__", None)
        defs.append(BeanDefinition(
            key=spec.key,
            owner_cls=cls,
            method_name=spec.name,
            deps=infer_deps(func),
            scope=spec.scope,
            source=source,
            conditions=merge_conditions(class_cond, method_cond),
            autoconfigure_name=auto.get("name"),
            order=auto.get("order", getattr(getattr(cls, "__hive__", None), "order", 0)),
            after=list(auto.get("after") or []),
            before=list(auto.get("before") or []),
            lazy=spec.scope == "request",
            primary=bool(getattr(raw, "__hive_primary__", False)),
        ))
    return defs
