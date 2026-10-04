from fastapi_hive.ioc_framework.hive_settings import (
    apply_convention,
    apply_updates,
    collect_hive_settings,
    normalize_key,
    parse_simple_yaml,
)
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


def test_normalize_key_accepts_aliases_and_env_prefix():
    assert normalize_key("HIVE_API_PREFIX") == "API_PREFIX"
    assert normalize_key("api-prefix") == "API_PREFIX"
    assert normalize_key("endpoint_package_paths") == "ENDPOINT_PACKAGE_PATHS"
    assert normalize_key("unknown") is None


def test_parse_simple_yaml_unwraps_hive_mapping():
    data = parse_simple_yaml(
        """
# comment
hive:
  api_prefix: /api
  hide_endpoint_in_tag: true
  endpoint_package_paths:
    - ./pkg1
    - ./pkg2
  features:
    notes: true
"""
    )
    assert data["api_prefix"] == "/api"
    assert data["hide_endpoint_in_tag"] is True
    assert data["endpoint_package_paths"] == ["./pkg1", "./pkg2"]
    assert data["features"] == {"notes": True}


def test_collect_hive_settings_prefers_env_over_file(tmp_path, monkeypatch):
    config_file = tmp_path / "hive.yaml"
    config_file.write_text(
        "api_prefix: /from-file\ncornerstone_package_path: ./from-file\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HIVE_API_PREFIX", "/from-env")
    monkeypatch.delenv("HIVE_CORNERSTONE_PACKAGE_PATH", raising=False)

    values = collect_hive_settings(
        config_path=str(config_file),
        roots=[tmp_path],
    )
    assert values["API_PREFIX"] == "/from-env"
    assert values["CORNERSTONE_PACKAGE_PATH"] == str(tmp_path / "from-file")


def test_constructor_overrides_win(tmp_path, monkeypatch):
    config_file = tmp_path / "hive.yaml"
    config_file.write_text("api_prefix: /from-file\n", encoding="utf-8")
    monkeypatch.setenv("HIVE_API_PREFIX", "/from-env")

    values = collect_hive_settings(
        config_path=str(config_file),
        overrides={"API_PREFIX": "/from-code"},
        roots=[tmp_path],
    )
    assert values["API_PREFIX"] == "/from-code"


def test_convention_discovers_package_folders(tmp_path):
    (tmp_path / "cornerstones").mkdir()
    (tmp_path / "endpoints").mkdir()
    values = {}
    apply_convention(values, roots=[tmp_path])
    assert values["CORNERSTONE_PACKAGE_PATH"] == str(tmp_path / "cornerstones")
    assert values["ENDPOINT_PACKAGE_PATHS"] == [str(tmp_path / "endpoints")]


def test_apply_updates_ignores_unknown_fields():
    config = IoCConfig()
    apply_updates(config, {
        "API_PREFIX": "/v2",
        "NOT_A_FIELD": "x",
    })
    assert config.API_PREFIX == "/v2"
