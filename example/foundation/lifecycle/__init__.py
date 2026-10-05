import anyio
from fastapi import FastAPI

from fastapi_hive.ioc_framework.foundation_container import FoundationMeta
from fastapi_hive.ioc_framework.foundation_hooks import FoundationHooks
from fastapi_hive.ioc_framework.decorators import component, foundation


@component(scope="request")
class RequestStamp:
    """One instance per request. Route handlers that inject it share that instance."""

    pass


def _threaded_marker():
    return "threaded"


@foundation(name="lifecycle", order=50, profiles=["demo"])
class LifecycleHooks(FoundationHooks):
    """Every foundation hook, sync and async, plus parameter injection."""

    def configure(self):
        self.app.state.hive_lifecycle = ["configure"]

    def before_endpoint_startup(self, app: FastAPI, foundation: FoundationMeta):
        app.state.hive_lifecycle.append(
            "before_endpoint_startup:" + foundation.name
        )

    async def after_endpoint_startup(self):
        marker = await anyio.to_thread.run_sync(_threaded_marker)
        self.app.state.hive_lifecycle.append("after_endpoint_startup:" + marker)

    def before_endpoint_shutdown(self):
        self.app.state.hive_lifecycle.append("before_endpoint_shutdown")

    async def after_endpoint_shutdown(self):
        self.app.state.hive_lifecycle.append("after_endpoint_shutdown")


@foundation(name="audit", order=10, profiles=["demo"], enabled_when="audit")
class AuditHooks(FoundationHooks):

    def before_endpoint_startup(self):
        self.app.state.hive_lifecycle.append("audit.before_startup")


@foundation(name="disabled_probe", enabled_when="missing_flag")
class DisabledProbe(FoundationHooks):

    def configure(self):
        raise RuntimeError("disabled foundation configure must not run")

    def before_endpoint_startup(self):
        self.app.state.hive_lifecycle.append("disabled.startup")


@foundation(name="off_profile", profiles=["never"])
class OffProfileHooks(FoundationHooks):

    def before_endpoint_startup(self):
        self.app.state.hive_lifecycle.append("off_profile.startup")
