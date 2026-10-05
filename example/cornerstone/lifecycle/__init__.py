import anyio
from fastapi import FastAPI

from fastapi_hive.ioc_framework.cornerstone_container import CornerstoneMeta
from fastapi_hive.ioc_framework.cornerstone_hooks import CornerstoneHooks
from fastapi_hive.ioc_framework.decorators import component, cornerstone


@component(scope="request")
class RequestStamp:
    """One instance per request. Route handlers that inject it share that instance."""

    pass


def _threaded_marker():
    return "threaded"


@cornerstone(name="lifecycle", order=50, profiles=["demo"])
class LifecycleHooks(CornerstoneHooks):
    """Every cornerstone hook, sync and async, plus parameter injection."""

    def configure(self):
        self.app.state.hive_lifecycle = ["configure"]

    def before_endpoint_startup(self, app: FastAPI, cornerstone: CornerstoneMeta):
        app.state.hive_lifecycle.append(
            "before_endpoint_startup:" + cornerstone.name
        )

    async def after_endpoint_startup(self):
        marker = await anyio.to_thread.run_sync(_threaded_marker)
        self.app.state.hive_lifecycle.append("after_endpoint_startup:" + marker)

    def before_endpoint_shutdown(self):
        self.app.state.hive_lifecycle.append("before_endpoint_shutdown")

    async def after_endpoint_shutdown(self):
        self.app.state.hive_lifecycle.append("after_endpoint_shutdown")


@cornerstone(name="audit", order=10, profiles=["demo"], enabled_when="audit")
class AuditHooks(CornerstoneHooks):

    def before_endpoint_startup(self):
        self.app.state.hive_lifecycle.append("audit.before_startup")


@cornerstone(name="disabled_probe", enabled_when="missing_flag")
class DisabledProbe(CornerstoneHooks):

    def configure(self):
        raise RuntimeError("disabled cornerstone configure must not run")

    def before_endpoint_startup(self):
        self.app.state.hive_lifecycle.append("disabled.startup")


@cornerstone(name="off_profile", profiles=["never"])
class OffProfileHooks(CornerstoneHooks):

    def before_endpoint_startup(self):
        self.app.state.hive_lifecycle.append("off_profile.startup")
