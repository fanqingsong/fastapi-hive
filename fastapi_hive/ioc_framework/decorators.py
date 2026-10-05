import inspect
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence, Tuple, Type, get_type_hints

from fastapi.params import Depends as DependsParam

from fastapi_hive.ioc_framework.beans import BeanCondition
from fastapi_hive.ioc_framework.registry import HiveKey


@dataclass
class HiveMeta:
    role: str
    name: str
    order: int = 0
    profiles: Optional[List[str]] = None
    enabled_when: Optional[str] = None
    prefix: Optional[str] = None
    tags: Optional[List[str]] = None
    mount: bool = True


@dataclass
class MountSpec:
    skip: bool = False
    prefix: Optional[str] = None
    tags: Optional[List[str]] = None
    explicit: bool = False


@dataclass
class RouterBinding:
    router: Any
    mount: MountSpec
    order: int = 0
    name: str = ""


def _attach(cls: type, role: str, name: str, order: int, profiles, enabled_when,
            prefix, tags, mount) -> type:
    cls.__hive__ = HiveMeta(
        role=role,
        name=name,
        order=order,
        profiles=list(profiles) if profiles else None,
        enabled_when=enabled_when,
        prefix=prefix,
        tags=list(tags) if tags else None,
        mount=mount,
    )
    return cls


LIFECYCLE_METHODS = frozenset({
    "configure",
    "pre_endpoint_startup",
    "post_endpoint_startup",
    "pre_endpoint_shutdown",
    "post_endpoint_shutdown",
    "pre_endpoint_call",
    "post_endpoint_call",
    "startup",
    "shutdown",
})


def cornerstone(name: str, order: int = 0, profiles: Optional[Sequence[str]] = None,
                enabled_when: Optional[str] = None) -> Callable:
    def wrap(cls: type) -> type:
        _attach(cls, "cornerstone", name, order, profiles, enabled_when, None, None, True)
        collect_providers(cls)
        return cls

    return wrap


def endpoint(name: str, order: int = 0, prefix: Optional[str] = None,
             tags: Optional[Sequence[str]] = None, mount: bool = True,
             profiles: Optional[Sequence[str]] = None,
             enabled_when: Optional[str] = None) -> Callable:
    def wrap(cls: type) -> type:
        _attach(cls, "endpoint", name, order, profiles, enabled_when, prefix, tags, mount)
        collect_providers(cls)
        return cls

    return wrap


def provides(key: Any, scope: str = "app") -> Callable:
    if scope not in ("app", "request", "transient"):
        raise ValueError(f"provides scope must be 'app', 'request' or 'transient', got {scope!r}")

    def wrap(fn: Callable) -> Callable:
        fn.__hive_provides__ = key
        fn.__hive_provides_scope__ = scope
        return fn

    return wrap


class Qualifier:
    def __init__(self, name: Any):
        self.name = name


def component(key: Any = None, scope: str = "app", primary: bool = False, lazy: bool = False) -> Callable:
    if scope not in ("app", "request", "transient"):
        raise ValueError(f"component scope must be 'app', 'request' or 'transient', got {scope!r}")

    def wrap(cls: type) -> type:
        cls.__hive_component__ = {
            "key": key if key is not None else cls,
            "scope": scope,
            "primary": primary,
            "lazy": lazy,
        }
        return cls

    return wrap


def autoconfigure(
    name: str,
    order: int = 0,
    after: Optional[Sequence[str]] = None,
    before: Optional[Sequence[str]] = None,
) -> Callable:
    def wrap(cls: type) -> type:
        existing = getattr(cls, "__hive_autoconfigure__", None) or {}
        cls.__hive_autoconfigure__ = {
            "name": name,
            "order": order,
            "after": list(after or existing.get("after") or []),
            "before": list(before or existing.get("before") or []),
            "conditions": existing.get("conditions") or getattr(cls, "__hive_conditional__", None),
        }
        collect_providers(cls)
        return cls

    return wrap


def conditional(
    on_import: Optional[str] = None,
    on_missing: Any = None,
    on_bean: Any = None,
    enabled_when: Optional[str] = None,
    profiles: Optional[Sequence[str]] = None,
    on_property: Optional[str] = None,
) -> Callable:
    condition = BeanCondition(
        on_import=on_import,
        on_missing=on_missing,
        on_bean=on_bean,
        enabled_when=enabled_when,
        profiles=list(profiles) if profiles else None,
        on_property=on_property,
    )

    def wrap(obj):
        auto = getattr(obj, "__hive_autoconfigure__", None)
        if isinstance(auto, dict):
            auto["conditions"] = condition
        obj.__hive_conditional__ = condition
        return obj

    return wrap


def _feature_enabled(features: dict, dotted: str) -> bool:
    current = features or {}
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return bool(current)


def is_enabled(meta: HiveMeta, config) -> bool:
    if meta.profiles and not (set(meta.profiles) & set(config.ACTIVE_PROFILES or [])):
        return False
    if meta.enabled_when and not _feature_enabled(config.FEATURES or {}, meta.enabled_when):
        return False
    return True


def collect_hooks(module, *, role: str) -> List[type]:
    if module is None:
        return []

    hooks: List[type] = []
    seen = set()
    for obj in list(vars(module).values()):
        if not isinstance(obj, type) or obj in seen:
            continue
        seen.add(obj)
        hive = getattr(obj, "__hive__", None)
        if hive is None or hive.role != role:
            continue
        hooks.append(obj)
    return hooks


def collect_routers(module, *, mount_spec: MountSpec, order: int = 0,
                    name: str = "") -> List[RouterBinding]:
    if module is None:
        return []
    from fastapi import APIRouter
    router = getattr(module, "router", None)
    if not isinstance(router, APIRouter):
        return []
    return [RouterBinding(router=router, mount=mount_spec, order=order, name=name)]


def endpoint_hook_order(classes: Sequence[type]) -> int:
    orders = [
        cls.__hive__.order
        for cls in classes
        if getattr(cls, "__hive__", None) is not None and cls.__hive__.role == "endpoint"
    ]
    return min(orders) if orders else 0


def select_routers(pairs: Sequence[Tuple["RouterBinding", Any]]) -> List[Tuple["RouterBinding", Any]]:
    chosen = [(binding, meta) for binding, meta in pairs if not binding.mount.skip]
    chosen.sort(key=lambda item: (item[0].order, item[0].name or getattr(item[1], "name", "")))
    return chosen


def resolve_router_target(meta, binding: RouterBinding, config) -> Tuple[str, List[str]]:
    prefix = f"{config.API_PREFIX}"
    if not config.HIDE_ENDPOINT_CONTAINER_IN_API:
        prefix = f"{prefix}/{meta.container_name}"
    if not config.HIDE_ENDPOINT_IN_API:
        prefix = f"{prefix}/{meta.name}"
    tag = f"{meta.container_name}"
    if not config.HIDE_ENDPOINT_IN_TAG:
        tag = f"{tag}.{meta.name}"
    mount = binding.mount
    if mount.explicit:
        if mount.prefix is not None:
            prefix = mount.prefix
        tags = mount.tags if mount.tags is not None else [tag]
    else:
        tags = [tag]
    return prefix, tags


def resolve_mount(classes: Sequence[type]) -> MountSpec:
    decorated = []
    for cls in classes:
        hive = getattr(cls, "__hive__", None)
        if hive is not None and hive.role == "endpoint":
            decorated.append(cls)
    if any(not cls.__hive__.mount for cls in decorated):
        return MountSpec(skip=True)
    for cls in decorated:
        hive = cls.__hive__
        if hive.prefix is not None or hive.tags is not None:
            return MountSpec(prefix=hive.prefix, tags=hive.tags, explicit=True)
    return MountSpec()


@dataclass
class ProviderSpec:
    name: str
    key: Any
    scope: str


def _callable_func(value: Any) -> Optional[Callable]:
    if isinstance(value, (staticmethod, classmethod)):
        return value.__func__
    if inspect.isfunction(value) or inspect.ismethod(value):
        return value
    return None


def collect_providers(cls: type) -> List[ProviderSpec]:
    specs = {}
    for klass in reversed(cls.__mro__):
        if klass is object:
            continue
        for name, value in klass.__dict__.items():
            func = _callable_func(value)
            if func is None:
                continue
            key = getattr(func, "__hive_provides__", None)
            if name in LIFECYCLE_METHODS and key is not None:
                raise TypeError(
                    f"{cls.__name__}.{name} is a lifecycle method and cannot use @provides"
                )
            if key is None:
                specs.pop(name, None)
                continue
            specs[name] = ProviderSpec(
                name=name,
                key=key,
                scope=getattr(func, "__hive_provides_scope__", "app"),
            )
    return list(specs.values())


def _hive_key_from_default(default: Any) -> Any:
    if isinstance(default, DependsParam) and isinstance(default.dependency, HiveKey):
        return default.dependency.key
    return None


def _context_get(context, key, request=None):
    if context is None:
        raise KeyError(f"Hive dependency {key!r} is not registered")
    if hasattr(context, "definitions"):
        return context.get(key, request)
    if hasattr(context, "has") and context.has(key):
        return context.get(key)
    raise KeyError(f"Hive dependency {key!r} is not registered")


def resolve_params(func: Callable, context, request=None, extras=None) -> dict:
    extras = extras or {}
    try:
        hints = get_type_hints(func, include_extras=True)
    except Exception:
        try:
            hints = get_type_hints(func)
        except Exception:
            hints = {}
    kwargs = {}
    for name, param in inspect.signature(func).parameters.items():
        if name == "self":
            continue
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        hive_key = _hive_key_from_default(param.default)
        if hive_key is not None:
            kwargs[name] = _context_get(context, hive_key, request)
            continue
        hint = hints.get(name)
        if hint is not None and hint in extras:
            kwargs[name] = extras[hint]
            continue
        if hint is not None:
            from fastapi_hive.ioc_framework.beans import qualifier_from_hint, unwrap_hint

            key = qualifier_from_hint(hint) or unwrap_hint(hint)
            if key in extras:
                kwargs[name] = extras[key]
                continue
            kwargs[name] = _context_get(context, key, request)
            continue
        if param.default is not inspect.Parameter.empty:
            continue
        raise TypeError(f"Cannot inject parameter {name!r} of {func.__qualname__}")
    return kwargs


def create_hook(cls: Type, context, extras=None, request=None) -> Any:
    kwargs = resolve_params(cls.__init__, context, request, extras)
    return cls(**kwargs)


def select_hooks(pairs: Sequence[Tuple[type, Any]], config) -> List[Tuple[type, Any]]:
    chosen = [(cls, meta) for cls, meta in pairs if is_enabled(cls.__hive__, config)]
    chosen.sort(key=lambda item: (item[0].__hive__.order, item[0].__hive__.name))
    return chosen


def call_injected_sync(method: Callable, context, request=None, extras=None):
    kwargs = resolve_params(method, context, request, extras)
    if inspect.iscoroutinefunction(method):
        raise TypeError(f"{method.__qualname__} must be synchronous")
    result = method(**kwargs)
    if inspect.isawaitable(result):
        raise TypeError(f"{method.__qualname__} must be synchronous")
    return result


async def call_injected(method: Callable, context, request=None, extras=None):
    kwargs = resolve_params(method, context, request, extras)
    result = method(**kwargs)
    if inspect.isawaitable(result):
        result = await result
    return result


def invoke_sync(instance: Any, method_name: str, context, request=None, extras=None):
    method = getattr(instance, method_name)
    return call_injected_sync(method, context, request, extras)


async def invoke(instance: Any, method_name: str, context, request=None, extras=None):
    method = getattr(instance, method_name)
    return await call_injected(method, context, request, extras)


def bind_cornerstone(instance: Any, app, meta, request=None) -> None:
    instance.app = app
    instance.cornerstone = meta
    if request is None:
        return
    instance.request = request


def bind_endpoint(instance: Any, app, meta) -> None:
    instance.app = app
    instance.endpoint = meta
