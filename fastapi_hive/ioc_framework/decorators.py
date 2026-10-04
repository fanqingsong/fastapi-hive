import inspect
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence, Tuple, Type, get_type_hints


_ASYNC_BASES = {"CornerstoneAsyncHooks", "EndpointAsyncHooks"}


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
    async_mode: bool = False
    legacy: bool = False


@dataclass
class MountSpec:
    skip: bool = False
    prefix: Optional[str] = None
    tags: Optional[List[str]] = None
    explicit: bool = False


def _async_mode(cls: type) -> bool:
    return any(base.__name__ in _ASYNC_BASES for base in cls.__mro__)


def _attach(cls: type, role: str, name: str, order: int, profiles, enabled_when,
            prefix, tags, mount, legacy: bool) -> type:
    cls.__hive__ = HiveMeta(
        role=role,
        name=name,
        order=order,
        profiles=list(profiles) if profiles else None,
        enabled_when=enabled_when,
        prefix=prefix,
        tags=list(tags) if tags else None,
        mount=mount,
        async_mode=_async_mode(cls),
        legacy=legacy,
    )
    return cls


def cornerstone(name: str, order: int = 0, profiles: Optional[Sequence[str]] = None,
                enabled_when: Optional[str] = None) -> Callable:
    def wrap(cls: type) -> type:
        return _attach(cls, "cornerstone", name, order, profiles, enabled_when, None, None, True, False)

    return wrap


def endpoint(name: str, order: int = 0, prefix: Optional[str] = None,
             tags: Optional[Sequence[str]] = None, mount: bool = True,
             profiles: Optional[Sequence[str]] = None,
             enabled_when: Optional[str] = None) -> Callable:
    def wrap(cls: type) -> type:
        return _attach(cls, "endpoint", name, order, profiles, enabled_when, prefix, tags, mount, False)

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


def collect_hooks(module, *, role: str, legacy_sync: str, legacy_async: str,
                  default_name: str) -> Tuple[List[type], List[type]]:
    if module is None:
        return [], []

    sync: List[type] = []
    async_hooks: List[type] = []
    seen = set()
    for obj in list(vars(module).values()):
        if not isinstance(obj, type) or obj in seen:
            continue
        seen.add(obj)
        hive = getattr(obj, "__hive__", None)
        if hive is None or hive.role != role or hive.legacy:
            continue
        (async_hooks if hive.async_mode else sync).append(obj)

    if not sync:
        legacy_cls = getattr(module, legacy_sync, None)
        if isinstance(legacy_cls, type):
            _attach(legacy_cls, role, default_name, 0, None, None, None, None, True, True)
            sync.append(legacy_cls)
    if not async_hooks:
        legacy_cls = getattr(module, legacy_async, None)
        if isinstance(legacy_cls, type):
            _attach(legacy_cls, role, default_name, 0, None, None, None, None, True, True)
            async_hooks.append(legacy_cls)
    return sync, async_hooks


def resolve_mount(classes: Sequence[type]) -> MountSpec:
    decorated = []
    for cls in classes:
        hive = getattr(cls, "__hive__", None)
        if hive is not None and hive.role == "endpoint" and not hive.legacy:
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


def invoke(instance: Any, method_name: str, app_registry, request_registry=None):
    method = getattr(instance, method_name)
    result = method()
    publish_provides(method, result, app_registry, request_registry)
    return result


async def invoke_async(instance: Any, method_name: str, app_registry, request_registry=None):
    method = getattr(instance, method_name)
    result = await method()
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
    state = request.state.cornerstones[pkg_path]
    if hasattr(instance, "request_state"):
        instance.request_state = state
    if hasattr(instance, "req_state"):
        instance.req_state = state


def bind_endpoint(instance: Any, app, meta) -> None:
    instance.app = app
    instance.endpoint = meta
    pkg_path = f"{meta.container_name}.{meta.name}"
    instance.app_state = app.state.endpoints[pkg_path]
