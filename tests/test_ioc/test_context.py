from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from starlette.testclient import TestClient

from fastapi_hive.ioc_framework.autowire import apply_autowire
from fastapi_hive.ioc_framework.beans import definition_from_component, definitions_from_class
from fastapi_hive.ioc_framework.context import HiveContext
from fastapi_hive.ioc_framework.decorators import component, provides
from fastapi_hive.ioc_framework.registry import HiveRegistry


class Engine:
    pass


class LateService:
    def __init__(self, engine: Engine):
        self.engine = engine


def test_creates_dependencies_regardless_of_definition_order():
    class Owner:
        @provides(LateService)
        def late(self, engine: Engine):
            return LateService(engine)

        @provides(Engine)
        def early(self):
            return Engine()

    context = HiveContext()
    context.add_definitions(definitions_from_class(Owner, "scan"))
    context.refresh()
    assert isinstance(context.get(LateService).engine, Engine)


def test_circular_dependency_fails():
    class Owner:
        @provides("a")
        def a(self, b: str = None):
            return "a"

    # force deps graph a -> b -> a
    from fastapi_hive.ioc_framework.beans import BeanDefinition, BeanCondition

    context = HiveContext()
    context.add_definitions([
        BeanDefinition(key="a", owner_cls=None, method_name=None, deps=["b"]),
        BeanDefinition(key="b", owner_cls=None, method_name=None, deps=["a"]),
    ])
    try:
        context.validate()
    except ValueError as exc:
        assert "circular" in str(exc)
    else:
        raise AssertionError("expected circular hive dependency")


def test_request_bean_is_lazy_until_get():
    created = {"count": 0}

    class Owner:
        @provides("session", scope="request")
        def session(self):
            created["count"] += 1
            return "sess"

    app = FastAPI()
    context = HiveContext(app)
    context.add_definitions(definitions_from_class(Owner, "scan"))
    context.refresh()
    assert created["count"] == 0

    request = type("Req", (), {"state": type("S", (), {})()})()
    request.state.hive = HiveRegistry()
    assert context.get("session", request) == "sess"
    assert created["count"] == 1
    assert context.get("session", request) == "sess"
    assert created["count"] == 1


def test_route_autowire_injects_beans_not_pydantic_body():
    @component()
    class Token:
        pass

    class Payload(BaseModel):
        name: str

    app = FastAPI()
    context = HiveContext(app)
    context.add_definitions([definition_from_component(Token)])
    context.refresh()
    app.state.hive = context

    router = APIRouter()

    def echo(payload: Payload, token: Token):
        return {"token": token is context.get(Token), "name": payload.name}

    router.add_api_route("/echo", apply_autowire(echo, context), methods=["POST"])
    app.include_router(router)

    with TestClient(app) as client:
        response = client.post("/echo", json={"name": "hive"})

    assert response.status_code == 200
    assert response.json() == {"token": True, "name": "hive"}
