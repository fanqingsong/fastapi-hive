import importlib
import importlib.util
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from fastapi_hive.ioc_framework.beans import (
    BeanCondition,
    BeanDefinition,
    definition_from_component,
    definitions_from_class,
)
from fastapi_hive.ioc_framework.decorators import _feature_enabled


def collect_from_module(module, source: str = "scan") -> Tuple[List[BeanDefinition], List[type]]:
    if module is None:
        return [], []
    definitions = []
    autos = []
    seen = set()
    for obj in list(vars(module).values()):
        if not isinstance(obj, type) or obj in seen:
            continue
        seen.add(obj)
        if getattr(obj, "__hive_autoconfigure__", None):
            autos.append(obj)
            definitions.extend(definitions_from_class(obj, source="autoconfigure"))
            if getattr(obj, "__hive_component__", None):
                definitions.append(definition_from_component(obj, source="autoconfigure"))
            continue
        if getattr(obj, "__hive_component__", None):
            definitions.append(definition_from_component(obj, source=source))
            continue
        hive = getattr(obj, "__hive__", None)
        if hive is not None:
            definitions.extend(definitions_from_class(obj, source=source))
    return definitions, autos


def collect_from_modules(modules: Iterable) -> Tuple[List[BeanDefinition], List[type]]:
    definitions = []
    autos = []
    seen_defs = set()
    seen_autos = set()
    for module in modules:
        defs, found = collect_from_module(module)
        for item in defs:
            token = (item.owner_cls, item.method_name, item.key)
            if token in seen_defs:
                continue
            seen_defs.add(token)
            definitions.append(item)
        for cls in found:
            if cls in seen_autos:
                continue
            seen_autos.add(cls)
            autos.append(cls)
    return definitions, autos


def load_entry_point_classes() -> List[Tuple[str, type]]:
    try:
        from importlib.metadata import entry_points
    except ImportError:  # pragma: no cover
        return []
    try:
        selected = entry_points().select(group="hive.autoconfigure")
    except AttributeError:
        selected = entry_points().get("hive.autoconfigure", [])
    loaded = []
    for item in selected:
        loaded.append((item.name, item.load()))
    return loaded


def load_dotted(path: str):
    if ":" in path:
        module_name, attr = path.split(":", 1)
    else:
        module_name, _, attr = path.rpartition(".")
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def collect_import_classes(paths: Sequence[str]) -> List[Tuple[str, type]]:
    loaded = []
    for path in paths or []:
        if not path or path in ("[]", ".",):
            continue
        cls = load_dotted(path)
        auto = getattr(cls, "__hive_autoconfigure__", None) or {}
        loaded.append((auto.get("name") or path, cls))
    return loaded


def _excluded(name: str, cls: type, exclude: Sequence[str]) -> bool:
    qual = f"{cls.__module__}:{cls.__name__}"
    dotted = f"{cls.__module__}.{cls.__name__}"
    return name in exclude or qual in exclude or dotted in exclude


def gather_autoconfigure_classes(
    scanned: Sequence[type],
    config,
) -> List[type]:
    if not getattr(config, "AUTOCONFIGURE_ENABLED", True):
        return []
    exclude = list(getattr(config, "AUTOCONFIGURE_EXCLUDE", None) or [])
    by_name: Dict[str, type] = {}
    for cls in scanned:
        auto = getattr(cls, "__hive_autoconfigure__", None) or {}
        name = auto.get("name") or cls.__name__
        if _excluded(name, cls, exclude):
            continue
        by_name[name] = cls
    for name, cls in load_entry_point_classes():
        auto = getattr(cls, "__hive_autoconfigure__", None) or {}
        name = auto.get("name") or name
        if _excluded(name, cls, exclude):
            continue
        by_name[name] = cls
    for name, cls in collect_import_classes(getattr(config, "AUTOCONFIGURE_IMPORTS", None) or []):
        if _excluded(name, cls, exclude):
            continue
        by_name[name] = cls
    return list(by_name.values())


def _property_enabled(config, dotted: str) -> bool:
    if "=" in dotted:
        key, _, expected = dotted.partition("=")
        current = (config.FEATURES or {})
        for part in key.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif hasattr(config, part):
                current = getattr(config, part)
            else:
                return False
        return str(current) == expected
    if hasattr(config, dotted):
        return bool(getattr(config, dotted))
    return _feature_enabled(config.FEATURES or {}, dotted)


def passes_static_condition(condition: Optional[BeanCondition], config) -> bool:
    condition = condition or BeanCondition()
    if condition.on_import and importlib.util.find_spec(condition.on_import) is None:
        return False
    if condition.profiles and not (set(condition.profiles) & set(config.ACTIVE_PROFILES or [])):
        return False
    if condition.enabled_when and not _feature_enabled(config.FEATURES or {}, condition.enabled_when):
        return False
    if condition.on_property and not _property_enabled(config, condition.on_property):
        return False
    return True


def sort_autoconfigure(classes: Sequence[type]) -> List[type]:
    infos = []
    for cls in classes:
        auto = getattr(cls, "__hive_autoconfigure__", None) or {}
        infos.append({
            "cls": cls,
            "name": auto.get("name") or cls.__name__,
            "order": auto.get("order", 0),
            "after": set(auto.get("after") or []),
            "before": set(auto.get("before") or []),
        })
    names = {item["name"] for item in infos}
    incoming = {item["name"]: 0 for item in infos}
    edges = {item["name"]: set() for item in infos}
    for item in infos:
        for after in item["after"]:
            if after in names:
                edges[after].add(item["name"])
                incoming[item["name"]] += 1
        for before in item["before"]:
            if before in names:
                edges[item["name"]].add(before)
                incoming[before] += 1
    ready = sorted(
        [item for item in infos if incoming[item["name"]] == 0],
        key=lambda item: (item["order"], item["name"]),
    )
    ordered = []
    while ready:
        item = ready.pop(0)
        ordered.append(item["cls"])
        for nxt in edges[item["name"]]:
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                ready.extend([info for info in infos if info["name"] == nxt])
                ready.sort(key=lambda info: (info["order"], info["name"]))
    if len(ordered) != len(infos):
        raise ValueError("circular hive autoconfigure after/before")
    return ordered


def scanned_modules(cornerstone_container, endpoint_container) -> List:
    modules = []
    for meta in cornerstone_container.cornerstones.values():
        modules.append(meta.imported_module)
    for meta in endpoint_container.endpoints.values():
        for module in getattr(meta, "imported_modules", None) or [meta.imported_module]:
            if module is not None:
                modules.append(module)
    return modules


def build_definitions(modules: Iterable, config) -> Tuple[List[BeanDefinition], List[type]]:
    definitions, scanned_autos = collect_from_modules(modules)
    extra_autos = gather_autoconfigure_classes(scanned_autos, config)
    seen = set(scanned_autos)
    for cls in extra_autos:
        if cls in seen:
            continue
        definitions.extend(definitions_from_class(cls, "autoconfigure"))
        if getattr(cls, "__hive_component__", None):
            definitions.append(definition_from_component(cls, "autoconfigure"))
    allowed = set(extra_autos)
    definitions = [
        item for item in definitions
        if item.source != "autoconfigure" or item.owner_cls in allowed
    ]
    return evaluate_definitions(definitions, config), extra_autos


def evaluate_definitions(definitions: Sequence[BeanDefinition], config) -> List[BeanDefinition]:
    static = [item for item in definitions if passes_static_condition(item.conditions, config)]
    scan = [item for item in static if item.source != "autoconfigure"]
    auto = [item for item in static if item.source == "autoconfigure"]
    groups: Dict[str, List[BeanDefinition]] = {}
    classes = []
    for item in auto:
        name = item.autoconfigure_name or (item.owner_cls.__name__ if item.owner_cls else item.key)
        groups.setdefault(str(name), []).append(item)
        if item.owner_cls and item.owner_cls not in classes:
            classes.append(item.owner_cls)
    if classes:
        ordered_names = []
        for cls in sort_autoconfigure(classes):
            auto_meta = getattr(cls, "__hive_autoconfigure__", None) or {}
            ordered_names.append(auto_meta.get("name") or cls.__name__)
        for name in groups:
            if name not in ordered_names:
                ordered_names.append(name)
    else:
        ordered_names = list(groups)
    accepted = list(scan)
    accepted_keys = {item.key for item in accepted}
    changed = True
    while changed:
        changed = False
        for name in ordered_names:
            for item in groups.get(name, []):
                if item in accepted:
                    continue
                cond = item.conditions or BeanCondition()
                if cond.on_bean is not None and cond.on_bean not in accepted_keys:
                    continue
                if cond.on_missing is not None and cond.on_missing in accepted_keys:
                    continue
                accepted.append(item)
                accepted_keys.add(item.key)
                changed = True
    return accepted
