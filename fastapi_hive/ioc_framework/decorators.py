import inspect
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence, Tuple, Type, get_type_hints


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


def cornerstone(name: str, order: int = 0, profiles: Optional[Sequence[str]] = None,
                enabled_when: Optional[str] = None) -> Callable:
    def wrap(cls: type) -> type:
        return _attach(cls, "cornerstone", name, order, profiles, enabled_when, None, None, True)

    return wrap


def endpoint(name: str, order: int = 0, prefix: Optional[str] = None,
             tags: Optional[Sequence[str]] = None, mount: bool = True,
             profiles: Optional[Sequence[str]] = None,
             enabled_when: Optional[str] = None) -> Callable:
    def wrap(cls: type) -> type:
        return _attach(cls, "endpoint", name, order, profiles, enabled_when, prefix, tags, mount)

    return wrap


def provides(key: Any) -> Callable:
    def wrap(fn: Callable) -> Callable:
        fn.__hive_provides__ = key
        return fn

    return wrap


def request_provides(key: Any) -> Callable:
    def wrap(fn: Callable) -> Callable:
        fn.__hive_request_provides__ = key
        return fn

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


def create_hook(cls: Type, registry) -> Any:
    try:
        hints = get_type_hints(cls.__init__)
    except Exception:
        hints = {}
    kwargs = {}
    signature = inspect.signature(cls.__init__)
    for name, param in signature.parameters.items():
        if name == "self":
            continue
        hint = hints.get(name)
        if hint is not None and registry is not None and registry.has(hint):
            kwargs[name] = registry.get(hint)
        elif param.default is inspect.Parameter.empty:
            continue
    return cls(**kwargs)


def select_hooks(pairs: Sequence[Tuple[type, Any]], config) -> List[Tuple[type, Any]]:
    chosen = [(cls, meta) for cls, meta in pairs if is_enabled(cls.__hive__, config)]
    chosen.sort(key=lambda item: (item[0].__hive__.order, item[0].__hive__.name))
    return chosen


def publish_provides(method: Callable, result: Any, app_registry, request_registry) -> None:
    if result is None:
        return
    func = getattr(method, "__func__", method)
    provide_key = getattr(func, "__hive_provides__", None)
    if provide_key is not None and app_registry is not None:
        app_registry.register(provide_key, result)
    request_key = getattr(func, "__hive_request_provides__", None)
    if request_key is not None and request_registry is not None:
        request_registry.register(request_key, result)


def invoke_sync(instance: Any, method_name: str, app_registry, request_registry=None):
    method = getattr(instance, method_name)
    if inspect.iscoroutinefunction(method):
        raise TypeError(
            f"{type(instance).__name__}.{method_name} must be synchronous"
        )
    result = method()
    if inspect.isawaitable(result):
        raise TypeError(
            f"{type(instance).__name__}.{method_name} must be synchronous"
        )
    publish_provides(method, result, app_registry, request_registry)
    return result


async def invoke(instance: Any, method_name: str, app_registry, request_registry=None):
    method = getattr(instance, method_name)
    result = method()
    if inspect.isawaitable(result):
        result = await result
    publish_provides(method, result, app_registry, request_registry)
    return result


def bind_cornerstone(instance: Any, app, meta, request=None) -> None:
    instance.app = app
    instance.cornerstone = meta
    pkg_path = f"{meta.container_name}.{meta.name}"
    instance.app_state = app.state.cornerstones[pkg_path]
    if request is None:
        return
    instance.request = request
    instance.request_state = request.state.cornerstones[pkg_path]


def bind_endpoint(instance: Any, app, meta) -> None:
    instance.app = app
    instance.endpoint = meta
    pkg_path = f"{meta.container_name}.{meta.name}"
    instance.app_state = app.state.endpoints[pkg_path]
