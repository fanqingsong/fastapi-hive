import asyncio
import types

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks
from fastapi_hive.ioc_framework.decorators import (
    collect_hooks,
    collect_providers,
    cornerstone,
    create_hook,
    endpoint,
    invoke,
    invoke_sync,
    provides,
    select_hooks,
)
from fastapi_hive.ioc_framework.beans import definitions_from_class
from fastapi_hive.ioc_framework.context import HiveContext
from fastapi_hive.ioc_framework.endpoint_hooks import EndpointHooks
from fastapi_hive.ioc_framework.ioc_config import IoCConfig
from fastapi_hive.ioc_framework.registry import Inject, HiveRegistry, resolve


def test_collect_decorated_hook_skips_undecorated_class():
    module = types.ModuleType("sample_hooks")

    @cornerstone(name="db", order=5)
    class DbHooks(CornerstoneHooks):
        pass

    class CornerstoneHooksImpl(CornerstoneHooks):
        pass

    module.DbHooks = DbHooks
    module.CornerstoneHooksImpl = CornerstoneHooksImpl

    hooks = collect_hooks(module, role="cornerstone")

    assert hooks == [DbHooks]


def test_undecorated_class_is_not_collected():
    module = types.ModuleType("legacy_hooks")

    class CornerstoneHooksImpl(CornerstoneHooks):
        pass

    module.CornerstoneHooksImpl = CornerstoneHooksImpl

    assert collect_hooks(module, role="cornerstone") == []


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


def test_provides_is_visible_through_inject():
    class Owner:
        @provides("model")
        def model(self):
            return "loaded"

    app = FastAPI()
    context = HiveContext(app)
    context.add_definitions(definitions_from_class(Owner, "scan"))
    context.refresh()
    app.state.hive = context

    @app.get("/model")
    def read_model(model: str = Inject("model")):
        return {"model": model}

    with TestClient(app) as client:
        response = client.get("/model")

    assert response.status_code == 200
    assert response.json() == {"model": "loaded"}


def test_depends_hive_invokes_request_callable():
    from starlette.requests import Request

    def checker(request: Request) -> str:
        return request.headers.get("x-name", "anon")

    app = FastAPI()
    app.state.hive = HiveRegistry()
    app.state.hive.register("auth.ok", checker)

    @app.get("/who")
    def who(name: str = Inject("auth.ok")):
        return {"name": name}

    with TestClient(app) as client:
        response = client.get("/who", headers={"x-name": "hive"})

    assert response.json() == {"name": "hive"}


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
    def read_item(item: str = Inject("item")):
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


def test_invoke_sync_rejects_async_configure():
    class Owner:
        async def configure(self):
            return "nope"

    with pytest.raises(TypeError, match="must be synchronous"):
        invoke_sync(Owner(), "configure", None)


def test_mixed_sync_configure_and_async_startup():
    class Mixed(CornerstoneHooks):
        @provides("db")
        def engine(self):
            return "engine"

        def configure(self):
            return "configured"

        async def before_endpoint_startup(self):
            return "ready"

    context = HiveContext()
    context.add_definitions(definitions_from_class(Mixed, "scan"))
    instance = Mixed()
    assert invoke_sync(instance, "configure", context) == "configured"
    context.refresh()
    assert context.get("db") == "engine"
    assert asyncio.run(invoke(instance, "before_endpoint_startup", context)) == "ready"


def test_class_can_publish_multiple_app_providers():
    class Owner:
        @provides("one")
        def first(self):
            return 1

        @provides("two")
        def second(self):
            return 2

    context = HiveContext()
    assert [spec.key for spec in collect_providers(Owner)] == ["one", "two"]
    context.add_definitions(definitions_from_class(Owner, "scan"))
    context.refresh()
    assert context.get("one") == 1
    assert context.get("two") == 2


def test_request_registry_overrides_app_in_resolve():
    app_registry = HiveRegistry()
    app_registry.register("item", "app")
    request_registry = HiveRegistry()
    request_registry.register("item", "request")
    assert resolve("item", app_registry, request_registry) == "request"


def test_hook_parameter_injection_from_type_and_inject():
    registry = HiveRegistry()
    registry.register("name", "hive")
    registry.register(Token, Token())

    class Owner:
        def startup(self, token: Token, name: str = Inject("name")):
            return token, name

    token, name = asyncio.run(invoke(Owner(), "startup", registry))
    assert isinstance(token, Token)
    assert name == "hive"


def test_provides_on_lifecycle_method_raises():
    with pytest.raises(TypeError, match="lifecycle method"):
        @endpoint(name="bad")
        class BadHooks(EndpointHooks):
            @provides("model")
            def startup(self):
                return "nope"


def test_missing_dependency_raises_key_error():
    with pytest.raises(KeyError, match="missing"):
        resolve("missing", HiveRegistry())


def test_create_hook_and_depends_hive_share_instance():
    registry = HiveRegistry()
    token = Token()
    registry.register(Token, token)
    instance = create_hook(NotesHooks, registry)
    assert instance.token is resolve(Token, registry)

    app = FastAPI()
    app.state.hive = registry

    @app.get("/token")
    def read_token(value: Token = Inject(Token)):
        return {"same": value is token}

    with TestClient(app) as client:
        assert client.get("/token").json() == {"same": True}
