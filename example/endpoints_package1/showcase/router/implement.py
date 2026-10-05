import sys

from fastapi import APIRouter
from starlette.requests import Request

from example.cornerstone.lifecycle import RequestStamp
from example.endpoints_package1.showcase.beans import LazyProbe, PrimaryGreeter
from fastapi_hive.ioc_framework.decorators import Qualifier, resolve_params
from fastapi_hive.ioc_framework.registry import Inject

try:
    from typing import Annotated
except ImportError:  # Python 3.8
    from typing_extensions import Annotated

router = APIRouter()


def read_qualified(
    formal: Annotated[str, Qualifier("greeting.formal")],
    casual: Annotated[str, Qualifier("greeting.casual")],
):
    return {"formal": formal, "casual": casual}


def _entry_points():
    try:
        from importlib.metadata import entry_points
    except ImportError:
        return []
    try:
        selected = entry_points().select(group="hive.autoconfigure")
    except AttributeError:
        selected = entry_points().get("hive.autoconfigure", [])
    return ["%s = %s" % (item.name, item.value) for item in selected]


def _qualified(hive, request):
    try:
        return resolve_params(read_qualified, hive, request)
    except Exception as exc:
        return {
            "error": exc.__class__.__name__,
            "python": "%s.%s" % sys.version_info[:2],
        }


@router.get("/tour", name="feature tour")
def feature_tour(
    request: Request,
    stamp: RequestStamp = Inject(RequestStamp),
    greeter: PrimaryGreeter = Inject("showcase.greeter"),
):
    hive = request.app.state.hive
    lazy_was_cached = hive.app_cache.has(LazyProbe)
    hive.get(LazyProbe)
    first_ticket = hive.get("showcase.ticket")
    second_ticket = hive.get("showcase.ticket")
    again = hive.get(RequestStamp, request)
    db_session = hive.get("db.session", request)
    db_session_again = hive.get("db.session", request)

    return {
        "path": "/api/showcase/tour",
        "scopes": {
            "primary": greeter.style,
            "primary_saw_import": greeter.imported,
            "request_shared": stamp is again,
            "db_session_shared": db_session is db_session_again,
            "transient": [first_ticket, second_ticket],
            "lazy_created_on_get": (
                lazy_was_cached is False and hive.app_cache.has(LazyProbe)
            ),
        },
        "conditions": {
            "imported": hive.get("showcase.imported"),
            "user_message": hive.get("showcase.user_message"),
            "excluded": hive.has("showcase.skipped"),
            "on_missing_blocked": hive.has("showcase.blocked"),
            "fallback": hive.get("showcase.fallback"),
            "on_bean": hive.get("showcase.auth_linked"),
            "on_import_blocked": hive.has("showcase.no_such_pkg"),
            "profile_demo": hive.has("showcase.on_demo"),
            "profile_never": hive.has("showcase.off_profile"),
            "enabled_when_audit": hive.has("showcase.audit"),
            "enabled_when_missing": hive.has("showcase.no_flag"),
            "on_property": hive.has("showcase.prefix_ok"),
            "on_property_miss": hive.has("showcase.bad_prefix"),
            "auth_registered": hive.has("auth.ok"),
            "db_registered": hive.has("db") and hive.has("db.session"),
        },
        "bean_order": list(getattr(request.app.state, "showcase_bean_order", [])),
        "qualifier": _qualified(hive, request),
        "hooks": {
            "lifecycle": list(request.app.state.hive_lifecycle),
            "endpoint": request.app.state.showcase_endpoint_name,
        },
        "autoconfigure": {
            "import_path": "example.starters.imported_auto:ImportedAuto",
            "entry_points": _entry_points(),
        },
    }
