import inspect
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from fastapi_hive.ioc_framework.ioc_config import IoCConfig


ENV_PREFIX = "HIVE_"
FOUNDATION_DIR_NAMES = ("foundation", "foundations")
ENDPOINT_DIR_NAMES = ("endpoints", "endpoint_packages")
DEFAULT_FOUNDATION_PATH = "./foundation"
DEFAULT_ENDPOINT_PATHS = ["./endpoints"]

_FIELD_ALIASES = {
    "foundation_package_path": "FOUNDATION_PACKAGE_PATH",
    "endpoint_package_paths": "ENDPOINT_PACKAGE_PATHS",
    "api_prefix": "API_PREFIX",
    "active_profiles": "ACTIVE_PROFILES",
    "features": "FEATURES",
    "autoconfigure_enabled": "AUTOCONFIGURE_ENABLED",
    "autoconfigure_imports": "AUTOCONFIGURE_IMPORTS",
    "autoconfigure_exclude": "AUTOCONFIGURE_EXCLUDE",
}


def _known_fields() -> Sequence[str]:
    fields = getattr(IoCConfig, "model_fields", None)
    if fields is None:
        fields = IoCConfig.__fields__
    return tuple(fields)


def normalize_key(name: str) -> Optional[str]:
    key = name.strip()
    if key.startswith(ENV_PREFIX):
        key = key[len(ENV_PREFIX):]
    snake = key.replace("-", "_")
    upper = snake.upper()
    if upper in _known_fields():
        return upper
    return _FIELD_ALIASES.get(snake.lower())


def _parse_scalar(raw: str) -> Any:
    text = raw.strip()
    if not text or text in ("~", "null", "Null", "NULL"):
        return None
    if text[0] in {'"', "'"} and text[-1] == text[0]:
        return text[1:-1]
    if text == "[]":
        return []
    if text == "{}":
        return {}
    lowered = text.lower()
    if lowered in ("true", "yes", "on"):
        return True
    if lowered in ("false", "no", "off"):
        return False
    if re.fullmatch(r"-?\d+", text):
        return int(text)
    return text


def _parse_env_value(field: str, raw: str) -> Any:
    text = raw.strip()
    if field == "FEATURES":
        return json.loads(text) if text else {}
    if field in ("ENDPOINT_PACKAGE_PATHS", "ACTIVE_PROFILES", "AUTOCONFIGURE_IMPORTS", "AUTOCONFIGURE_EXCLUDE"):
        if text.startswith("["):
            return json.loads(text)
        if not text:
            return []
        return [item.strip() for item in text.split(",") if item.strip()]
    return _parse_scalar(text)


def _flatten_nested(data: Dict[str, Any]) -> Dict[str, Any]:
    flattened = dict(data)
    autoconfigure = flattened.pop("autoconfigure", None)
    if isinstance(autoconfigure, dict):
        if "enabled" in autoconfigure:
            flattened["autoconfigure_enabled"] = autoconfigure["enabled"]
        if "imports" in autoconfigure:
            flattened["autoconfigure_imports"] = autoconfigure["imports"]
        if "exclude" in autoconfigure:
            flattened["autoconfigure_exclude"] = autoconfigure["exclude"]
    return flattened


def normalize_mapping(data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {}
    for key, value in _flatten_nested(data).items():
        field = normalize_key(str(key))
        if field is None:
            continue
        normalized[field] = value
    return normalized


def load_dotenv_hive_vars(path: Path) -> Dict[str, Any]:
    values = {}
    if not path.is_file():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        field = normalize_key(key)
        if field is None:
            continue
        values[field] = _parse_env_value(field, value)
    return values


def load_process_env() -> Dict[str, Any]:
    values = {}
    for key, value in os.environ.items():
        if not key.startswith(ENV_PREFIX):
            continue
        field = normalize_key(key)
        if field is None:
            continue
        values[field] = _parse_env_value(field, value)
    return values


def _unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen = set()
    unique = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def _is_library_frame(filename: str) -> bool:
    normalized = filename.replace("\\", "/")
    if filename.startswith("<"):
        return True
    library_markers = (
        "fastapi_hive",
        "/site-packages/",
        "/dist-packages/",
    )
    return any(marker in normalized for marker in library_markers)


def discover_roots() -> List[Path]:
    roots = [Path.cwd()]
    for frame in inspect.stack():
        if _is_library_frame(frame.filename):
            continue
        roots.append(Path(frame.filename).resolve().parent)
        break
    return _unique_paths(roots)


def _first_existing_dir(roots: Sequence[Path], names: Sequence[str]) -> Optional[str]:
    for root in roots:
        for name in names:
            candidate = root / name
            if candidate.is_dir():
                return str(candidate)
    return None


def apply_convention(values: Dict[str, Any], roots: Optional[Sequence[Path]] = None):
    search_roots = list(roots) if roots is not None else discover_roots()
    foundation = values.get("FOUNDATION_PACKAGE_PATH", DEFAULT_FOUNDATION_PATH)
    uses_default_foundation = foundation == DEFAULT_FOUNDATION_PATH
    if not foundation or (uses_default_foundation and not os.path.isdir(foundation)):
        found = _first_existing_dir(search_roots, FOUNDATION_DIR_NAMES)
        if found:
            values["FOUNDATION_PACKAGE_PATH"] = found

    endpoints = values.get("ENDPOINT_PACKAGE_PATHS", DEFAULT_ENDPOINT_PATHS)
    uses_default_endpoints = endpoints == DEFAULT_ENDPOINT_PATHS
    missing_default = uses_default_endpoints and not os.path.isdir(endpoints[0])
    if not endpoints or missing_default:
        found = _first_existing_dir(search_roots, ENDPOINT_DIR_NAMES)
        if found:
            values["ENDPOINT_PACKAGE_PATHS"] = [found]


def resolve_package_paths(values: Dict[str, Any], base: Path) -> None:
    foundation = values.get("FOUNDATION_PACKAGE_PATH")
    if isinstance(foundation, str) and foundation:
        values["FOUNDATION_PACKAGE_PATH"] = _path_beside(foundation, base)
    endpoints = values.get("ENDPOINT_PACKAGE_PATHS")
    if isinstance(endpoints, list):
        values["ENDPOINT_PACKAGE_PATHS"] = [
            _path_beside(item, base) if isinstance(item, str) else item
            for item in endpoints
        ]


def _path_beside(value: str, base: Path) -> str:
    path = Path(value)
    if path.is_absolute():
        return value
    located = base / path
    try:
        relative = located.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return str(located)
    text = relative.as_posix()
    if text == ".":
        return "./"
    return "./" + text


def dump_config(config: IoCConfig) -> Dict[str, Any]:
    if hasattr(config, "model_dump"):
        return config.model_dump()
    return config.dict()


def apply_updates(config: IoCConfig, updates: Dict[str, Any]) -> IoCConfig:
    for field, value in updates.items():
        if field not in _known_fields():
            continue
        setattr(config, field, value)
    return config


def collect_hive_settings(
    overrides: Optional[Dict[str, Any]] = None,
    roots: Optional[Sequence[Path]] = None,
) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    search_roots = list(roots) if roots is not None else discover_roots()
    for root in search_roots:
        values.update(load_dotenv_hive_vars(root / ".env"))
    values.update(load_process_env())
    if overrides:
        mapped = normalize_mapping(overrides)
        resolve_package_paths(mapped, search_roots[-1] if search_roots else Path.cwd())
        values.update(mapped)
    apply_convention(values, roots)
    return values


def apply_hive_settings(
    config: IoCConfig,
    overrides: Optional[Dict[str, Any]] = None,
    roots: Optional[Sequence[Path]] = None,
) -> IoCConfig:
    updates = collect_hive_settings(
        overrides=overrides,
        roots=roots,
    )
    return apply_updates(config, updates)
