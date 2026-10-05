from fastapi_hive.ioc_framework.hive_settings import (
    apply_convention,
    apply_updates,
    collect_hive_settings,
    normalize_key,
    normalize_mapping,
)
from fastapi_hive.ioc_framework.ioc_config import IoCConfig


def test_normalize_key_accepts_aliases_and_env_prefix():
    assert normalize_key("HIVE_API_PREFIX") == "API_PREFIX"
    assert normalize_key("api-prefix") == "API_PREFIX"
    assert normalize_key("endpoint_package_paths") == "ENDPOINT_PACKAGE_PATHS"
    assert normalize_key("unknown") is None


def test_normalize_mapping_flattens_autoconfigure():
    values = normalize_mapping({
        "features": {"db": True},
        "autoconfigure": {"enabled": True, "imports": [], "exclude": ["hive.db"]},
        "runners": {"imports": ["example.starters.seed_runner:SeedDataRunner"]},
    })
    assert values["FEATURES"] == {"db": True}
    assert values["AUTOCONFIGURE_ENABLED"] is True
    assert values["AUTOCONFIGURE_IMPORTS"] == []
    assert values["AUTOCONFIGURE_EXCLUDE"] == ["hive.db"]
    assert values["RUNNER_IMPORTS"] == ["example.starters.seed_runner:SeedDataRunner"]


def test_collect_hive_settings_ignores_yaml_file(tmp_path, monkeypatch):
    (tmp_path / "hive.yaml").write_text(
        "api_prefix: /from-file\nfoundation_package_path: ./from-file\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("HIVE_API_PREFIX", raising=False)
    monkeypatch.delenv("HIVE_FOUNDATION_PACKAGE_PATH", raising=False)

    values = collect_hive_settings(roots=[tmp_path])
    assert "API_PREFIX" not in values
    assert values.get("FOUNDATION_PACKAGE_PATH") != str(tmp_path / "from-file")


def test_settings_paths_resolve_beside_caller(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    app_dir = tmp_path / "myapp"
    (app_dir / "foundation").mkdir(parents=True)
    (app_dir / "endpoints_package1").mkdir()

    values = collect_hive_settings(
        overrides={
            "foundation_package_path": "./foundation",
            "endpoint_package_paths": ["./endpoints_package1"],
        },
        roots=[tmp_path, app_dir],
    )
    assert values["FOUNDATION_PACKAGE_PATH"] == "./myapp/foundation"
    assert values["ENDPOINT_PACKAGE_PATHS"] == ["./myapp/endpoints_package1"]


def test_constructor_overrides_win(tmp_path, monkeypatch):
    monkeypatch.setenv("HIVE_API_PREFIX", "/from-env")

    values = collect_hive_settings(
        overrides={"API_PREFIX": "/from-code"},
        roots=[tmp_path],
    )
    assert values["API_PREFIX"] == "/from-code"


def test_convention_discovers_package_folders(tmp_path):
    (tmp_path / "foundations").mkdir()
    (tmp_path / "endpoints").mkdir()
    values = {}
    apply_convention(values, roots=[tmp_path])
    assert values["FOUNDATION_PACKAGE_PATH"] == str(tmp_path / "foundations")
    assert values["ENDPOINT_PACKAGE_PATHS"] == [str(tmp_path / "endpoints")]


def test_apply_updates_ignores_unknown_fields():
    config = IoCConfig()
    apply_updates(config, {
        "API_PREFIX": "/v2",
        "NOT_A_FIELD": "x",
    })
    assert config.API_PREFIX == "/v2"
