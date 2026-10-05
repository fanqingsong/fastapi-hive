import inspect
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from fastapi_hive.ioc_framework.ioc_config import IoCConfig


CONFIG_FILENAMES = ("hive.yaml", "hive.yml", "hive.json")
ENV_PREFIX = "HIVE_"
CORNERSTONE_DIR_NAMES = ("cornerstone", "cornerstones")
ENDPOINT_DIR_NAMES = ("endpoints", "endpoint_packages")
DEFAULT_CORNERSTONE_PATH = "./cornerstone"
DEFAULT_ENDPOINT_PATHS = ["./endpoints"]
CALLABLE_FIELDS = {
    "PRE_ENDPOINT_STARTUP",
    "POST_ENDPOINT_STARTUP",
    "PRE_ENDPOINT_SHUTDOWN",
    "POST_ENDPOINT_SHUTDOWN",
    "ASYNC_PRE_ENDPOINT_STARTUP",
    "ASYNC_POST_ENDPOINT_STARTUP",
    "ASYNC_PRE_ENDPOINT_SHUTDOWN",
    "ASYNC_POST_ENDPOINT_SHUTDOWN",
}

_FIELD_ALIASES = {
    "cornerstone_package_path": "CORNERSTONE_PACKAGE_PATH",
    "endpoint_package_paths": "ENDPOINT_PACKAGE_PATHS",
    "api_prefix": "API_PREFIX",
    "active_profiles": "ACTIVE_PROFILES",
    "features": "FEATURES",
    "router_mount_automated": "ROUTER_MOUNT_AUTOMATED",
    "hide_endpoint_container_in_api": "HIDE_ENDPOINT_CONTAINER_IN_API",
    "hide_endpoint_in_api": "HIDE_ENDPOINT_IN_API",
    "hide_endpoint_in_tag": "HIDE_ENDPOINT_IN_TAG",
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
    if field in ("ENDPOINT_PACKAGE_PATHS", "ACTIVE_PROFILES"):
        if text.startswith("["):
            return json.loads(text)
        if not text:
            return []
        return [item.strip() for item in text.split(",") if item.strip()]
    return _parse_scalar(text)


def _line_indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _parse_mapping(lines: List[str], start: int, indent: int):
    data: Dict[str, Any] = {}
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        current = _line_indent(line)
        if current < indent:
            break
        if current > indent:
            raise ValueError("invalid hive.yaml indentation")
        stripped = line.strip()
        if stripped.startswith("- "):
            break
        key, _, rest = stripped.partition(":")
        rest = rest.strip()
        index += 1
        if rest:
            data[key] = _parse_scalar(rest)
            continue
        if index < len(lines) and lines[index].lstrip().startswith("- "):
            values, index = _parse_list(lines, index, current + 2)
            data[key] = values
        else:
            nested, index = _parse_mapping(lines, index, current + 2)
            data[key] = nested
    return data, index


def _parse_list(lines: List[str], start: int, indent: int):
    values: List[Any] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        current = _line_indent(line)
        if current < indent - 2:
            break
        stripped = line.strip()
        if not stripped.startswith("- "):
            break
        values.append(_parse_scalar(stripped[2:]))
        index += 1
    return values, index


def parse_simple_yaml(text: str) -> Dict[str, Any]:
    lines = text.replace("\t", "  ").splitlines()
    data, _ = _parse_mapping(lines, 0, 0)
    hive = data.get("hive")
    if isinstance(hive, dict):
        return hive
    return data


def parse_config_file(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text) or {}
    else:
        data = parse_simple_yaml(text)
    if isinstance(data.get("hive"), dict):
        data = data["hive"]
    return normalize_mapping(data)


def normalize_mapping(data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {}
    for key, value in data.items():
        field = normalize_key(str(key))
        if field is None or field in CALLABLE_FIELDS:
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
        if field is None or field in CALLABLE_FIELDS:
            continue
        values[field] = _parse_env_value(field, value)
    return values


def load_process_env() -> Dict[str, Any]:
    values = {}
    for key, value in os.environ.items():
        if not key.startswith(ENV_PREFIX):
            continue
        field = normalize_key(key)
        if field is None or field in CALLABLE_FIELDS:
            continue
        values[field] = _parse_env_value(field, value)
    return values


def find_config_file(
    config_path: Optional[str] = None,
    roots: Optional[Sequence[Path]] = None,
) -> Optional[Path]:
    if config_path:
        path = Path(config_path)
        if not path.is_file():
            raise FileNotFoundError(f"hive config file not found: {path}")
        return path
    env_path = os.environ.get("HIVE_CONFIG")
    if env_path:
        path = Path(env_path)
        if not path.is_file():
            raise FileNotFoundError(f"hive config file not found: {path}")
        return path
    search_roots = list(roots) if roots is not None else discover_roots()
    for root in search_roots:
        for name in CONFIG_FILENAMES:
            candidate = root / name
            if candidate.is_file():
                return candidate
    return None


def resolve_package_paths(values: Dict[str, Any], base: Path) -> None:
    cornerstone = values.get("CORNERSTONE_PACKAGE_PATH")
    if isinstance(cornerstone, str) and cornerstone:
        values["CORNERSTONE_PACKAGE_PATH"] = _path_beside(cornerstone, base)
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
    cornerstone = values.get("CORNERSTONE_PACKAGE_PATH", DEFAULT_CORNERSTONE_PATH)
    uses_default_cornerstone = cornerstone == DEFAULT_CORNERSTONE_PATH
    if not cornerstone or (uses_default_cornerstone and not os.path.isdir(cornerstone)):
        found = _first_existing_dir(search_roots, CORNERSTONE_DIR_NAMES)
        if found:
            values["CORNERSTONE_PACKAGE_PATH"] = found

    endpoints = values.get("ENDPOINT_PACKAGE_PATHS", DEFAULT_ENDPOINT_PATHS)
    uses_default_endpoints = endpoints == DEFAULT_ENDPOINT_PATHS
    missing_default = uses_default_endpoints and not os.path.isdir(endpoints[0])
    if not endpoints or missing_default:
        found = _first_existing_dir(search_roots, ENDPOINT_DIR_NAMES)
        if found:
            values["ENDPOINT_PACKAGE_PATHS"] = [found]


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
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None,
    roots: Optional[Sequence[Path]] = None,
) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    file_path = find_config_file(config_path, roots=roots)
    if file_path is not None:
        values.update(parse_config_file(file_path))
        resolve_package_paths(values, file_path.parent)
    search_roots = list(roots) if roots is not None else discover_roots()
    for root in search_roots:
        values.update(load_dotenv_hive_vars(root / ".env"))
    values.update(load_process_env())
    if overrides:
        values.update(normalize_mapping(overrides))
    apply_convention(values, roots)
    return values


def apply_hive_settings(
    config: IoCConfig,
    config_path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None,
    roots: Optional[Sequence[Path]] = None,
) -> IoCConfig:
    updates = collect_hive_settings(
        config_path=config_path,
        overrides=overrides,
        roots=roots,
    )
    return apply_updates(config, updates)
