import types

from fastapi import FastAPI
from starlette.testclient import TestClient

from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks
from fastapi_hive.ioc_framework.decorators import (
    collect_hooks,
    cornerstone,
    create_hook,
    endpoint,
    invoke,
    provides,
    select_hooks,
)
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi_hive.ioc_framework.registry import DependsHive, HiveRegistry


def test_collect_decorated_hook_skips_legacy_class():
    module = types.ModuleType("sample_hooks")

    @cornerstone(name="db", order=5)
    class DbHooks(CornerstoneHooks):
        pass

    class CornerstoneHooksImpl(CornerstoneHooks):
        pass

    module.DbHooks = DbHooks
    module.CornerstoneHooksImpl = CornerstoneHooksImpl

    sync, async_hooks = collect_hooks(
        module,
        role="cornerstone",
        legacy_sync="CornerstoneHooksImpl",
        legacy_async="CornerstoneAsyncHooksImpl",
        default_name="db",
    )

    assert sync == [DbHooks]
    assert async_hooks == []
    assert sync[0].__hive__.legacy is False


def test_legacy_class_name_is_collected():
    module = types.ModuleType("legacy_hooks")

    class CornerstoneHooksImpl(CornerstoneHooks):
        pass

    module.CornerstoneHooksImpl = CornerstoneHooksImpl

    sync, async_hooks = collect_hooks(
        module,
        role="cornerstone",
        legacy_sync="CornerstoneHooksImpl",
        legacy_async="CornerstoneAsyncHooksImpl",
        default_name="db",
    )

    assert sync == [CornerstoneHooksImpl]
    assert async_hooks == []
    assert sync[0].__hive__.legacy is True
    assert sync[0].__hive__.order == 0
    assert sync[0].__hive__.name == "db"


def test_select_hooks_sorts_and_filters():
    @cornerstone(name="late", order=10)
    class Late(CornerstoneHooks):
        pass

    @cornerstone(name="early", order=1, profiles=["prod"])
    class Early(CornerstoneHooks):
        pass

    @cornerstone(name="flagged", order=0, enabled_when="features.notes")
    class Flagged(CornerstoneHooks):
        pass

    disabled = IoCConfig(ACTIVE_PROFILES=["dev"], FEATURES={"features": {"notes": False}})
    selected = select_hooks([(Early, None), (Late, None), (Flagged, None)], disabled)
    assert [cls.__hive__.name for cls, _ in selected] == ["late"]

    enabled = IoCConfig(ACTIVE_PROFILES=["prod"], FEATURES={"features": {"notes": True}})
    selected = select_hooks([(Flagged, None), (Early, None), (Late, None)], enabled)
    assert [cls.__hive__.name for cls, _ in selected] == ["flagged", "early", "late"]


def test_provides_is_visible_through_depends_hive():
    class Owner:
        @provides("model")
        def setup(self):
            return "loaded"

    app = FastAPI()
    app.state.hive = HiveRegistry()
    invoke(Owner(), "setup", app.state.hive)

    @app.get("/model")
    def read_model(model: str = DependsHive("model")):
        return {"model": model}

    with TestClient(app) as client:
        response = client.get("/model")

    assert response.status_code == 200
    assert response.json() == {"model": "loaded"}


def test_depends_hive_prefers_request_registry():
    app = FastAPI()
    app.state.hive = HiveRegistry()
    app.state.hive.register("item", "app")

    @app.middleware("http")
    async def add_request_hive(request, call_next):
        request.state.hive = HiveRegistry()
        request.state.hive.register("item", "request")
        return await call_next(request)

    @app.get("/item")
    def read_item(item: str = DependsHive("item")):
        return {"item": item}

    with TestClient(app) as client:
        response = client.get("/item")

    assert response.json() == {"item": "request"}


class Token:
    pass


@endpoint(name="notes")
class NotesHooks(EndpointHooks):
    def __init__(self, token: Token):
        super().__init__()
        self.token = token


def test_constructor_injection_uses_registry():
    registry = HiveRegistry()
    token = Token()
    registry.register(Token, token)

    instance = create_hook(NotesHooks, registry)

    assert instance.token is token
