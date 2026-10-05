import pytest

from fastapi_hive.ioc_framework.autoconfigure import scanned_modules
from fastapi_hive.ioc_framework.endpoint_container import (
    EndpointContainer,
    import_package_tree,
)


def _write_flat_endpoint(root):
    endpoint = root / "demo"
    schemas = endpoint / "schemas"
    schemas.mkdir(parents=True)
    (root / "__init__.py").write_text("")
    (endpoint / "__init__.py").write_text("")
    (schemas / "__init__.py").write_text(
        "from fastapi import APIRouter\n"
        "from fastapi_hive.ioc_framework.decorators import component\n"
        "\n"
        "router = APIRouter()\n"
        "\n"
        "@component()\n"
        "class Marker:\n"
        "    pass\n"
    )


def test_import_package_tree_walks_nested_modules(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    _write_flat_endpoint(tmp_path / "epkg")

    modules = import_package_tree("epkg.demo")
    names = {module.__name__ for module in modules}
    assert names == {"epkg.demo", "epkg.demo.schemas"}


def test_endpoint_scan_finds_component_and_router_without_db_router_service(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    _write_flat_endpoint(tmp_path / "epkg")

    container = EndpointContainer()
    container.register_endpoint_package_paths(["epkg"])
    container.load_endpoints()

    meta = container.endpoints["epkg.demo"]
    module_names = {module.__name__ for module in meta.imported_modules}
    assert "epkg.demo.schemas" in module_names

    class Foundations:
        foundations = {}

    modules = scanned_modules(Foundations(), container)
    markers = [
        obj
        for module in modules
        for obj in vars(module).values()
        if isinstance(obj, type) and getattr(obj, "__hive_component__", None)
    ]
    assert [cls.__name__ for cls in markers] == ["Marker"]


def test_reexported_component_is_registered_once(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    endpoint = tmp_path / "epkg" / "demo"
    inner = endpoint / "inner"
    inner.mkdir(parents=True)
    (tmp_path / "epkg" / "__init__.py").write_text("")
    (endpoint / "__init__.py").write_text("from epkg.demo.inner import Marker\n")
    (inner / "__init__.py").write_text(
        "from fastapi_hive.ioc_framework.decorators import component\n"
        "\n"
        "@component()\n"
        "class Marker:\n"
        "    pass\n"
    )

    container = EndpointContainer()
    container.register_endpoint_package_paths(["epkg"])
    container.load_endpoints()

    from fastapi_hive.ioc_framework.autoconfigure import collect_from_modules

    definitions, _ = collect_from_modules(container.endpoints["epkg.demo"].imported_modules)
    keys = [item.key for item in definitions if getattr(item.owner_cls, "__name__", "") == "Marker"]
    assert len(keys) == 1


def test_endpoint_hook_in_package_root_is_collected(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    endpoint = tmp_path / "rootpkg" / "demo"
    endpoint.mkdir(parents=True)
    (tmp_path / "rootpkg" / "__init__.py").write_text("")
    (endpoint / "__init__.py").write_text(
        "from fastapi_hive.ioc_framework.decorators import endpoint\n"
        "from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks\n"
        "\n"
        "@endpoint(name='demo')\n"
        "class DemoHooks(EndpointHooks):\n"
        "    pass\n"
    )
    (endpoint / "router.py").write_text("router = object()\n")

    container = EndpointContainer()
    container.register_endpoint_package_paths(["rootpkg"])
    container.load_endpoints()

    hooks = container.endpoints["rootpkg.demo"].hooks
    assert [cls.__name__ for cls in hooks] == ["DemoHooks"]


def test_endpoint_hook_in_submodule_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    endpoint = tmp_path / "nestedpkg" / "demo"
    router = endpoint / "router"
    router.mkdir(parents=True)
    (tmp_path / "nestedpkg" / "__init__.py").write_text("")
    (endpoint / "__init__.py").write_text("")
    (router / "__init__.py").write_text(
        "from fastapi_hive.ioc_framework.decorators import endpoint\n"
        "from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks\n"
        "\n"
        "@endpoint(name='demo')\n"
        "class DemoHooks(EndpointHooks):\n"
        "    pass\n"
    )

    container = EndpointContainer()
    container.register_endpoint_package_paths(["nestedpkg"])
    with pytest.raises(TypeError, match="endpoint package root"):
        container.load_endpoints()

