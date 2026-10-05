"""Bean graph used by GET /api/showcase/tour.

Covers @component (primary, lazy, app scope), @provides scopes, @conditional
(on_import, on_missing, on_bean, enabled_when, profiles, on_property), and
autoconfigure after/before. ``showcase.skipped`` is removed by
AUTOCONFIGURE_EXCLUDE in hive.yaml.
"""

from fastapi import FastAPI

from fastapi_hive.ioc_framework.decorators import (
    autoconfigure,
    component,
    conditional,
    provides,
)
from fastapi_hive.ioc_framework.registry import Inject


def _remember(app: FastAPI, name: str) -> str:
    order = getattr(app.state, "showcase_bean_order", None)
    if order is None:
        order = []
        app.state.showcase_bean_order = order
    order.append(name)
    return name


@component(key="showcase.greeter")
class QuietGreeter:
    style = "quiet"


@component(key="showcase.greeter", primary=True)
class PrimaryGreeter:
    style = "primary"

    def __init__(self, imported: str = Inject("showcase.imported")):
        self.imported = imported


@component(lazy=True)
class LazyProbe:
    created = True


_tickets = {"n": 0}


@autoconfigure(name="showcase.tickets")
class TicketAuto:

    @provides("showcase.ticket", scope="transient")
    def ticket(self):
        _tickets["n"] += 1
        return _tickets["n"]


@autoconfigure(name="showcase.greeting")
class GreetingAuto:

    @provides("greeting.formal")
    def formal(self):
        return "Hello"

    @provides("greeting.casual")
    def casual(self):
        return "Hi"


@autoconfigure(name="showcase.first", order=50, before=["showcase.second"])
class FirstAuto:

    @provides("showcase.first")
    def value(self, app: FastAPI):
        return _remember(app, "first")


@autoconfigure(name="showcase.second", order=0)
class SecondAuto:

    @provides("showcase.second")
    def value(self, app: FastAPI):
        return _remember(app, "second")


@autoconfigure(name="showcase.third", order=0, after=["showcase.second"])
class ThirdAuto:

    @provides("showcase.third")
    def value(self, app: FastAPI):
        return _remember(app, "third")


@autoconfigure(name="showcase.blocked")
@conditional(on_missing="showcase.user_message")
class BlockedByUserBean:
    """Skipped because the endpoint class already provides that key."""

    @provides("showcase.blocked")
    def value(self):
        return "should-not-exist"


@autoconfigure(name="showcase.fallback")
@conditional(on_missing="showcase.absent_key")
class FallbackAuto:

    @provides("showcase.fallback")
    def value(self):
        return "filled-because-missing"


@autoconfigure(name="showcase.when_auth", after=["hive.auth"])
@conditional(on_bean="auth.ok")
class WhenAuthAuto:

    @provides("showcase.auth_linked")
    def value(self):
        return "auth-present"


@autoconfigure(name="showcase.no_such_pkg")
@conditional(on_import="definitely_not_a_real_pkg_xyz")
class MissingImportAuto:

    @provides("showcase.no_such_pkg")
    def value(self):
        return "should-not-exist"


@autoconfigure(name="showcase.on_demo")
@conditional(profiles=["demo"])
class DemoProfileAuto:

    @provides("showcase.on_demo")
    def value(self):
        return True


@autoconfigure(name="showcase.off_profile")
@conditional(profiles=["never"])
class OffProfileAuto:

    @provides("showcase.off_profile")
    def value(self):
        return True


@autoconfigure(name="showcase.audit_bean")
@conditional(enabled_when="audit")
class AuditBeanAuto:

    @provides("showcase.audit")
    def value(self):
        return True


@autoconfigure(name="showcase.no_flag")
@conditional(enabled_when="missing_flag")
class MissingFlagAuto:

    @provides("showcase.no_flag")
    def value(self):
        return True


@autoconfigure(name="showcase.on_prefix")
@conditional(on_property="API_PREFIX=/api")
class PrefixMatchAuto:

    @provides("showcase.prefix_ok")
    def value(self):
        return True


@autoconfigure(name="showcase.bad_prefix")
@conditional(on_property="API_PREFIX=/nope")
class PrefixMissAuto:

    @provides("showcase.bad_prefix")
    def value(self):
        return True


@autoconfigure(name="showcase.skipped")
class SkippedAuto:
    """Present on disk, removed by hive.autoconfigure.exclude."""

    @provides("showcase.skipped")
    def value(self):
        return "should-be-excluded"
