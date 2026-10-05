import sys

from starlette.testclient import TestClient

from example.main import get_app


def test_feature_tour_covers_hive_capabilities(test_client) -> None:
    first = test_client.get("/api/showcase/tour")
    assert first.status_code == 200, first.text
    assert first.headers.get("x-process-time")
    body = first.json()

    assert body["path"] == "/api/showcase/tour"
    assert body["scopes"]["primary"] == "primary"
    assert body["scopes"]["primary_saw_import"] == "imported-by-config"
    assert body["scopes"]["request_shared"] is True
    assert body["scopes"]["db_session_shared"] is True
    tickets = body["scopes"]["transient"]
    assert tickets[1] == tickets[0] + 1
    assert body["scopes"]["lazy_created_on_get"] is True

    conditions = body["conditions"]
    assert conditions["imported"] == "imported-by-config"
    assert conditions["user_message"] == "from-user"
    assert conditions["excluded"] is False
    assert conditions["on_missing_blocked"] is False
    assert conditions["fallback"] == "filled-because-missing"
    assert conditions["on_bean"] == "auth-present"
    assert conditions["on_import_blocked"] is False
    assert conditions["profile_demo"] is True
    assert conditions["profile_never"] is False
    assert conditions["enabled_when_audit"] is True
    assert conditions["enabled_when_missing"] is False
    assert conditions["on_property"] is True
    assert conditions["on_property_miss"] is False
    assert conditions["auth_registered"] is True
    assert conditions["db_registered"] is True

    assert body["bean_order"] == ["first", "second", "third"]
    assert body["hooks"]["endpoint"] == "showcase"
    assert body["autoconfigure"]["import_path"].endswith("ImportedAuto")

    if sys.version_info >= (3, 9):
        assert body["qualifier"] == {"formal": "Hello", "casual": "Hi"}
    else:
        assert "error" in body["qualifier"]

    trace = body["hooks"]["lifecycle"]
    assert trace[0] == "configure"
    assert "disabled.startup" not in trace
    assert "off_profile.startup" not in trace
    assert "parked.startup" not in trace
    assert "gated.startup" not in trace
    assert trace.index("audit.before_startup") < trace.index("before_endpoint_startup:lifecycle")
    assert trace.index("before_endpoint_startup:lifecycle") < trace.index("showcase.startup")
    assert trace.index("showcase.startup") < trace.index("manual.startup")
    assert trace.index("manual.startup") < trace.index("after_endpoint_startup:threaded")

    manual = test_client.get("/api/manual/ping")
    assert manual.status_code == 200
    assert manual.json() == {"mounted": "startup"}
    assert test_client.get("/api/manual_mount/ping").status_code == 404
    assert test_client.get("/api/parked/ping").status_code == 404
    assert test_client.get("/api/gated/ping").status_code == 404

    listed = test_client.get("/hive/routers").json()
    paths = {item["path"] for item in listed}
    assert "/api/showcase/tour" in paths
    assert "/api/manual/ping" in paths
    assert "/api/hb2/heartbeat" in paths
    assert "/api/parked/ping" not in paths
    assert "/api/gated/ping" not in paths

    heartbeat = test_client.get("/api/hb2/heartbeat")
    assert heartbeat.status_code == 200
    assert heartbeat.json() == {"is_alive": True}


def test_shutdown_hooks_run_in_order() -> None:
    app = get_app()
    with TestClient(app):
        assert "showcase.startup" in app.state.hive_lifecycle
    trace = app.state.hive_lifecycle
    assert trace.index("before_endpoint_shutdown") < trace.index("showcase.shutdown")
    assert trace.index("showcase.shutdown") < trace.index("after_endpoint_shutdown")
